import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk

from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__

class ErrorDialog(Gtk.Dialog):
    def __init__(self,parent):
        pass
    def showNotInstalledError(self,win):
        dialog = Gtk.MessageDialog(
            win, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't load libinput-gestures")
        dialog.format_secondary_text(
            "Make sure it is correctly installed. The configuration file has been saved anyway.")
        dialog.run()
        dialog.destroy()
