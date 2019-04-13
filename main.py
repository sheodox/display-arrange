import gi
import pprint
import quickgtk
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import screenops as so

pp = pprint.PrettyPrinter(indent=4)


class DisplayArrangeWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Display Arrange")
        self.set_border_width(10)
        self.top_container = quickgtk.new_vbox()
        self.add(self.top_container)

        self.so = so.ScreenOps()
        self.render()

    def render(self):
        quickgtk.empty(self.top_container)
        self.render_favorites()
        self.render_new_favorite()
        self.show_all()

    def render_favorites(self):
        hbox = quickgtk.new_hbox()

        self.fav_model = self.so.get_favorites_as_list_store()
        self.fav_cb = Gtk.ComboBox.new_with_model(self.fav_model)
        fav_render = Gtk.CellRendererText()
        self.fav_cb.pack_start(fav_render, True)
        self.fav_cb.add_attribute(fav_render, "text", 0)
        self.fav_cb.set_active(self.so.find_index_of_current())

        apply_button = Gtk.Button(label='Apply')
        apply_button.connect("clicked", self.apply_arrangement)

        delete_button = Gtk.Button(label='Delete')
        delete_button.connect("clicked", self.delete_arrangement)

        quickgtk.add_all(hbox, [
            Gtk.Label('Select a favorite arrangement'),
            self.fav_cb,
            apply_button,
            delete_button
        ])
        self.top_container.add(hbox)

    def render_new_favorite(self):
        hbox = quickgtk.new_hbox()
        _, new_name_entry, fav_button = quickgtk.add_all(hbox, [
            Gtk.Label('Favorite the current screen arrangement'),
            Gtk.Entry(),
            Gtk.Button("Save")
        ])
        self.top_container.add(hbox)

        def new_fav(_):
            self.so.favorite_current(new_name_entry.get_text())
            self.render()

        fav_button.connect('clicked', new_fav)

    def get_selected_favorite_name(self):
        fav_iter = self.fav_cb.get_active_iter()

        if fav_iter is not None:
            return self.fav_model[fav_iter][0]

    def apply_arrangement(self, _):
        name = self.get_selected_favorite_name()
        if (name):
            self.so.apply(name)

    def delete_arrangement(self, _):
        name = self.get_selected_favorite_name()
        if (name):
            self.so.delete(name)
            self.render()



win = DisplayArrangeWindow()
win.connect('destroy', Gtk.main_quit)
Gtk.main()
