import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk

from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__


