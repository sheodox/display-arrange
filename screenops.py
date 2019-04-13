import gi
import os
import re
import json
import subprocess
from pathlib import Path
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


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

    def find_name_of_current(self):
        current = self.get_current_xrandr_settings()
        for index, fav in enumerate(self.favorites):
            if current == fav['monitors']:
                return fav['name']

    def find_favorite(self, name):
        return next((item for item in self.favorites if item['name'] == name), None)

    def apply(self, name):
        arrangement = self.find_favorite(name)
        if arrangement:
            self.run(self.build_xrandr_apply(arrangement['monitors']))

    def build_xrandr_apply(self, monitors):
        cmd = 'xrandr'
        for monitor in monitors:
            cmd += ' --output {} --mode {}x{} --pos {}x{}'.format(monitor['monitor_name'], monitor['res_w'], monitor['res_h'], monitor['axis_x'], monitor['axis_y'])
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

    def get_favorites_as_list(self):
        return list(item['name'] for item in self.favorites)

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

