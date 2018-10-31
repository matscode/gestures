import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

from .window_main import *

appid = "org.cunidev.gestures"

class Gestures(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id=appid,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, data=None):
        isWayland = (getenv("XDG_SESSION_TYPE")  == "wayland")
        if(isWayland):
            print("WARNING: xdotool and wmctrl are *NOT* supported by Wayland, meaning keyboard shortcuts and _internal commands will be ignored.\n\n")

        win = MainWindow(isWayland)
        win.set_position(Gtk.WindowPosition.CENTER)

        self.add_window(win)
        
        win.initialize()
            
        win.show_all()
    
    
    
