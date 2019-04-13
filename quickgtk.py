import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


def new_hbox():
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)


def new_vbox():
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL)


def add_all(container, children):
    for child in children:
        container.add(child)
    return tuple(children)


def empty(container):
    for child in container.get_children():
        container.remove(child)
