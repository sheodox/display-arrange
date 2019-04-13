import gi
import quickgtk
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import screenops as so


class QuickSelect(Gtk.Window):

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
        self.show_all()

    def render_favorites(self):
        vbox = quickgtk.new_vbox()

        quickgtk.add_all(vbox, [
            Gtk.Label('Select a favorite arrangement')
        ])

        current = self.so.find_name_of_current()
        print(current)
        first_btn = None
        for fav in self.so.get_favorites_as_list():
            btn = Gtk.RadioButton.new_with_label_from_widget(first_btn, fav)
            vbox.add(btn)
            if not first_btn:
                first_btn = btn
            btn.set_active(fav == current)
            btn.connect('toggled', self.apply_arrangement, fav)

        self.top_container.add(vbox)

    def apply_arrangement(self, button, name):
        if button.get_active():
            self.so.apply(name)
            Gtk.main_quit()
            quit(0)



win = QuickSelect()
win.connect('destroy', Gtk.main_quit)
Gtk.main()
