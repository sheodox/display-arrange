import gi
import re
import os
import json
import subprocess
import pprint
import quickgtk
from pathlib import Path

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

pp = pprint.PrettyPrinter(indent=4)


class DisplayArrangeWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Display Arrange")
        self.top_container = quickgtk.new_vbox()
        self.add(self.top_container)

        self.so = ScreenOps()
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
            self.fav_cb,
            apply_button,
            delete_button
        ])
        self.top_container.add(hbox)

    def render_new_favorite(self):
        hbox = quickgtk.new_hbox()
        new_name_entry, fav_button = quickgtk.add_all(hbox, [
            Gtk.Entry(),
            Gtk.Button("Favorite the current arrangement")
        ])
        self.top_container.add(hbox)

        def new_fav(_):
            self.so.favorite_current(new_name_entry.get_text())
            self.render()

        fav_button.connect('clicked', new_fav)

    def get_selected_favorite_name(self):
        fav_iter = self.fav_cb.get_active_iter()
        print(fav_iter)

        if fav_iter != None:
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


class ScreenOps:
    def __init__(self):
        save_folder = os.path.join(Path.home(), '.config/sheodox/display-arrange')
        os.makedirs(save_folder, exist_ok=True)
        self._save_path = os.path.join(save_folder, 'favorites.json')

        self.regex = {
            "monitor_info": re.compile(
                r'(?P<monitor_name>[\w\d-]+) connected (primary )?(?P<res_w>\d+)x(?P<res_h>\d+)\+(?P<axis_x>\d+)\+(?P<axis_y>\d+)',
                re.M)
        }

        self.favorites = []
        self.load()

    def find_index_of_current(self):
        current = self.get_current_xrandr_settings()
        for index, fav in enumerate(self.favorites):
            if current == fav['monitors']:
                return index


    def find_favorite(self, name):
        return next((item for item in self.favorites if item['name'] == name), None)

    def apply(self, name):
        arrangement = self.find_favorite(name)
        pp.pprint(arrangement)
        if arrangement:
            self.run(self.build_xrandr_apply(arrangement['monitors']))

    def build_xrandr_apply(self, monitors):
        cmd = 'xrandr'
        for monitor in monitors:
            cmd += ' --output {} --mode {}x{} --pos {}x{}'.format(monitor['monitor_name'], monitor['res_w'], monitor['res_h'], monitor['axis_x'], monitor['axis_y'])
        print(cmd)
        return cmd

    def delete(self, name):
        arrangement = self.find_favorite(name)
        if arrangement:
            self.favorites.remove(arrangement)
            self.save()

    def save(self):
        with open(self._save_path, 'w') as file:
            json.dump(self.favorites, file)

    def load(self):
        try:
            with open(self._save_path, 'r') as file:
                self.favorites = json.load(file)
        except FileNotFoundError:
            pass

    def get_favorites_as_list_store(self):
        store = Gtk.ListStore(str)
        for favorite in self.favorites:
            store.append([favorite["name"]])
        return store

    def get_current_xrandr_settings(self):
        monitors = []
        xrandr_list_monitors = [s for s in self.run('xrandr --query').split('\n') if ' connected ' in s]
        for monitor in xrandr_list_monitors:
            monitors.append(
                self.regex['monitor_info'].search(monitor).groupdict()
            )
        return monitors


    def favorite_current(self, name):
        self.favorites.append({
            'name': name,
            'monitors': self.get_current_xrandr_settings()
        })
        self.save()

    @staticmethod
    def run(cmd):
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8').stdout


win = DisplayArrangeWindow()
win.connect('destroy', Gtk.main_quit)
Gtk.main()
