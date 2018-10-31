import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gestures.configfile import ConfigFileHandler


class PreferencesDialog(Gtk.Dialog):
    def __init__(self,parent, confFile):
        self.confFile = confFile
        Gtk.Dialog.__init__(self, "Preferences", parent, 0, Gtk.ButtonsType.NONE)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(480, 100)
        self.connect("destroy", self.onDestroy)
        area = self.get_content_area()

        if(self.confFile.swipe_threshold != None):
            value = self.confFile.swipe_threshold
        else:
            value = 0

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin = 10)
        area.add(box)

        label = Gtk.Label("Swipe threshold")
        slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(value, 0, 100, 5, 10, 0))
        slider.connect("value-changed", self.onSwipeThresholdChanged)
        slider.set_hexpand(True)
        slider.set_digits(0)

        box.add(label)
        box.add(slider)

        area.show_all()

    def onSwipeThresholdChanged(self, widget):
        value = int(widget.get_value())
        if(value >= 0 and value <= 100):
            self.confFile.swipe_threshold = value

    def onDestroy(self, window):
        self.confFile.save()

class UnsupportedLinesDialog(Gtk.Dialog):
    def __init__(self, parent, confFile):
        Gtk.Dialog.__init__(self, "Edit unsupported lines", parent, 0, Gtk.ButtonsType.NONE)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(480, 200)
        area = self.get_content_area()


        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)

        cancelButton = Gtk.Button("Cancel")
        cancelButton.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse('red'))
        hb.pack_start(cancelButton)

        confirmButton = Gtk.Button("Confirm")
        confirmButton.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse('teal'))
        hb.pack_end(confirmButton)
        self.set_titlebar(hb)

        confirmButton.connect("clicked", self.onConfirm)
        cancelButton.connect("clicked", self.onCancel)
        

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        area.add(scrolledwindow)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()

        lines = '\n'.join(confFile.validUnsupportedLines[1:])
        self.textbuffer.set_text(lines)
        scrolledwindow.add(self.textview)

        self.show_all()


    def onCancel(self, widget):
        self.response(Gtk.ResponseType.CANCEL)

    def onConfirm(self, widget):
        self.response(Gtk.ResponseType.OK)
        
