import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk

from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__, appid, authors

class AppAboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self, parent=parent)

        
        self.set_program_name("Gestures")
        self.set_comments("A minimal, modern Gtk+ app for Linux touchpad gestures, based on the popular libinput-gestures tool.")
        self.set_version(__version__)
        
        try:
            self.set_logo(Gtk.IconTheme.get_default().load_icon(appid, 128, 0))
        except:
            pass
        
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_authors(authors)
        self.set_website("https://gitlab.com/cunidev")
        self.set_website_label("cunidev's GitLab")
        self.set_title("")

        self.connect('response', self.hide_dialog)
        self.connect('delete-event', self.hide_dialog)

    def hide_dialog(self, widget=None, event=None):
        self.hide()
        return True