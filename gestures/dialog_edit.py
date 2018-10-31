import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk
from copy import deepcopy

from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__


default_command = "notify-send \"Gesture performed\""

class EditDialog(Gtk.Dialog):
    def __init__(self, parent, confFile, i=-1):
        self.lock = False
        self.confFile = confFile

        if (i == -1):
            title = "Add Gesture"
            self.curGesture = Gesture("swipe", "up", default_command, 2)
        else:
            title = "Edit Gesture"
            self.curGesture = deepcopy(self.confFile.gestures[i])

        Gtk.Dialog.__init__(self, title, parent, 0, Gtk.ButtonsType.NONE)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(480, 200)

        area = self.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=15, margin=10)
        area.add(box)

        hbox = Gtk.Box(spacing=5)
        box.add(hbox)

        label = Gtk.Label()
        label.set_markup("<b>Type</b>")
        hbox.pack_start(label, False, False, 0)

        self.buttonTypeSwipe = Gtk.RadioButton.new_with_label_from_widget(
            None, "Swipe")
        hbox.pack_start(self.buttonTypeSwipe, False, False, 0)

        self.buttonTypePinch = Gtk.RadioButton.new_from_widget(
            self.buttonTypeSwipe)
        self.buttonTypePinch.set_label("Pinch")
        hbox.pack_start(self.buttonTypePinch, False, False, 0)

        self.buttonTypeSwipe.set_active((self.curGesture.type != "pinch"))
        self.buttonTypePinch.set_active((self.curGesture.type == "pinch"))

        directionBox = Gtk.Box(spacing=5)
        box.add(directionBox)

        label = Gtk.Label()
        label.set_markup("<b>Direction</b>")
        directionBox.pack_start(label, False, False, 0)

        self.buttonDirection1 = Gtk.RadioButton.new_with_label_from_widget(
            None, "Up")
        directionBox.pack_start(self.buttonDirection1, False, False, 0)

        self.buttonDirection2 = Gtk.RadioButton.new_from_widget(
            self.buttonDirection1)
        self.buttonDirection2.set_label("Down")
        directionBox.pack_start(self.buttonDirection2, False, False, 0)

        self.buttonDirection3 = Gtk.RadioButton.new_from_widget(
            self.buttonDirection1)
        self.buttonDirection3.set_label("Left")
        directionBox.pack_start(self.buttonDirection3, False, False, 0)

        self.buttonDirection4 = Gtk.RadioButton.new_from_widget(
            self.buttonDirection1)
        self.buttonDirection4.set_label("Right")
        directionBox.pack_start(self.buttonDirection4, False, False, 0)

        # 1: up/in 2: down/out 3: left/clockwise 4: right/anticlockwise
        self.buttonDirection1.set_active(
            (self.curGesture.direction == "up") or (self.curGesture.direction == "in"))
        self.buttonDirection2.set_active(
            (self.curGesture.direction == "down") or (self.curGesture.direction == "out"))
        self.buttonDirection3.set_active((self.curGesture.direction == "left") or (
            self.curGesture.direction == "clockwise"))
        self.buttonDirection4.set_active((self.curGesture.direction == "right") or (
            self.curGesture.direction == "anticlockwise"))

        hbox = Gtk.Box(spacing=5)
        box.add(hbox)

        label = Gtk.Label()
        label.set_markup("<b>Fingers</b>")
        hbox.pack_start(label, False, False, 0)

        self.buttonFinger2 = Gtk.RadioButton.new_with_label_from_widget(
            None, "Two")
        hbox.pack_start(self.buttonFinger2, False, False, 0)

        self.buttonFinger3 = Gtk.RadioButton.new_from_widget(
            self.buttonFinger2)
        self.buttonFinger3.set_label("Three")
        hbox.pack_start(self.buttonFinger3, False, False, 0)

        self.buttonFinger4 = Gtk.RadioButton.new_from_widget(
            self.buttonFinger2)
        self.buttonFinger4.set_label("Four")
        hbox.pack_start(self.buttonFinger4, False, False, 0)

        if (self.curGesture.fingers != 0):
            self.buttonFinger2.set_active((int(self.curGesture.fingers) == 2))
            self.buttonFinger3.set_active((int(self.curGesture.fingers) == 3))
            self.buttonFinger4.set_active((int(self.curGesture.fingers) == 4))

        hbox = Gtk.Box(spacing=5)
        box.add(hbox)

        label = Gtk.Label()
        label.set_markup("<b>Command</b>")
        hbox.pack_start(label, False, False, 0)


        suggestions = [
            'xdotool key [code] # simulate keystroke',
            '_internal ws_[direction] # switch workspace',
            'nohup [name] # launch GUI app',
            'notify_send [text] # send notification'
            ]
        for gesture in self.confFile.gestures:
            suggestions.append(gesture.command)

        suggestions = list(set(suggestions)) # remove duplicates

        liststore = Gtk.ListStore(str)
        for s in suggestions:
            liststore.append([s])

        completion = Gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)

        self.commandInput = Gtk.Entry()
        self.commandInput.set_completion(completion)
        self.commandInput.set_text(self.curGesture.command)
        hbox.pack_start(self.commandInput, True, True, 0)

        # header bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(False)
        hb.props.title = title

        cancelButton = Gtk.Button("Cancel")
        cancelButton.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse('red'))
        hb.pack_start(cancelButton)

        confirmButton = Gtk.Button("Confirm")
        confirmButton.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse('teal'))
        hb.pack_end(confirmButton)
        self.set_titlebar(hb)

        # signals - declared at the end to avoid AttributeErrors on not-yet-existing objects

        self.buttonTypeSwipe.connect("toggled", self.onTypeToggle, i, "swipe")
        self.buttonTypePinch.connect("toggled", self.onTypeToggle, i, "pinch")

        self.buttonDirection1.connect("toggled", self.onDirectionToggle, 1)
        self.buttonDirection2.connect("toggled", self.onDirectionToggle, 2)
        self.buttonDirection3.connect("toggled", self.onDirectionToggle, 3)
        self.buttonDirection4.connect("toggled", self.onDirectionToggle, 4)

        self.buttonFinger2.connect("toggled", self.onFingerToggle, 2)
        self.buttonFinger3.connect("toggled", self.onFingerToggle, 3)
        self.buttonFinger4.connect("toggled", self.onFingerToggle, 4)
        self.commandInput.connect("changed", self.onCommandChange)

        confirmButton.connect("clicked", self.onConfirm, i)
        cancelButton.connect("clicked", self.onCancel)
        
        confirmButton.set_can_default(True)
        confirmButton.grab_default()
        
        self.show_all()
        
        # SET LABELS - after show_all because of set_visible()
        self.setFingerRadios(self.curGesture.type)
        self.setDirectionLabels(self.curGesture.type)


    def setDirectionLabels(self, type):
        if(type == "pinch"):
            self.buttonDirection1.set_label("In")
            self.buttonDirection2.set_label("Out")
            self.buttonDirection3.set_label("Clockwise")
            self.buttonDirection4.set_label("Anticlockwise")
        else:
            self.buttonDirection1.set_label("Up")
            self.buttonDirection2.set_label("Down")
            self.buttonDirection3.set_label("Left")
            self.buttonDirection4.set_label("Right")

    def onTypeToggle(self, widget, i, type):
        self.curGesture.type = type

        self.setDirectionLabels(type)  # needed after changing type
        self.setFingerRadios(type)
        self.correctDirections()

    def setFingerRadios(self, type):
        if(type == "pinch"):
            self.buttonFinger2.set_visible(True)
        else:
            if(self.buttonFinger2.get_active() == True):
                self.buttonFinger3.set_active(True)
                
            self.buttonFinger2.set_visible(False)

    def correctDirections(self):
        if(self.buttonDirection2.get_active()):
            direction = 2
        elif(self.buttonDirection3.get_active()):
            direction = 3
        elif(self.buttonDirection4.get_active()):
            direction = 4
        else:
            direction = 1

        self.onDirectionToggle(None, direction)

    def onDirectionToggle(self, widget, direction):
        if(self.curGesture.type == "pinch"):
            if(direction == 2):
                self.curGesture.direction = "out"
            elif(direction == 3):
                self.curGesture.direction = "clockwise"
            elif(direction == 4):
                self.curGesture.direction = "anticlockwise"
            else:
                self.curGesture.direction = "in"  # first case as default
        else:
            if(direction == 2):
                self.curGesture.direction = "down"
            elif(direction == 3):
                self.curGesture.direction = "left"
            elif(direction == 4):
                self.curGesture.direction = "right"
            else:
                self.curGesture.direction = "up"  # first case as default

    def onFingerToggle(self, widget, finger):
        self.curGesture.fingers = finger

    def onCommandChange(self, widget):
        self.curGesture.command = widget.get_text()

    def onCancel(self, widget):
        self.response(Gtk.ResponseType.CANCEL)

    def onConfirm(self, widget, i):
        if(i != -1):
            self.confFile.gestures[i] = self.curGesture
        else:
            self.confFile.gestures.append(self.curGesture)
        self.confFile.save()
        try:
            self.confFile.reloadProcess()
        except:
            err = ErrorDialog(self)
            err.showNotInstalledError(self)
        
        self.response(Gtk.ResponseType.OK)