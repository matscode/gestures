import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Gdk

import sys, shlex, copy
from subprocess import Popen, call
from os.path import expanduser
from os import getenv
from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__

appid = "org.cunidev.gestures"
default_command = "notify-send \"Gesture performed\""

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
        


class EditDialog(Gtk.Dialog):
    def __init__(self, parent, confFile, i=-1):
        self.lock = False
        self.confFile = confFile

        if (i == -1):
            title = "Add Gesture"
            self.curGesture = Gesture("swipe", "up", default_command, 2)
        else:
            title = "Edit Gesture"
            self.curGesture = copy.deepcopy(self.confFile.gestures[i])

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

        self.commandInput = Gtk.Entry()
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


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, isWayland = False):
        self.isWayland = isWayland
        self.editMode = False
        # window
        Gtk.Window.__init__(self, title="Gestures")

        # header bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Gestures"
        if(self.isWayland):
            hb.props.subtitle = "(wayland session, no xdotool)"

        self.set_titlebar(hb)
        
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        hb.pack_end(button)
        button.connect("clicked", self.showMenu)

        self.menuPopover = Gtk.Popover.new(button)
        self.menuPopover.set_size_request(250, 100)
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        label = Gtk.Label(margin=12)
        label.set_markup("<b>Gestures</b> " + __version__)
        popoverBox.add(label)

        separator = Gtk.Separator(margin=5)
        popoverBox.add(separator)

        button = Gtk.Button("Edit unsupported")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onEditFile)
        #popoverBox.add(button)

        button = Gtk.Button("Edit manually")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onEditFileExternal)
        popoverBox.add(button)

        button = Gtk.Button("About")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onAbout)
        popoverBox.add(button)
        
        separator = Gtk.Separator(margin=5)
        popoverBox.add(separator)

        btnImport = Gtk.Button.new_from_icon_name("document-open", Gtk.IconSize.SMALL_TOOLBAR)
        btnImport.set_property("tooltip-text", "Import")
        btnImport.connect("clicked", self.importFile)
        
        btnExport = Gtk.Button.new_from_icon_name("document-save", Gtk.IconSize.SMALL_TOOLBAR)
        btnExport.set_property("tooltip-text", "Export")
        btnExport.connect("clicked", self.exportFile)
        
        btnRestore = Gtk.Button.new_from_icon_name("document-revert", Gtk.IconSize.SMALL_TOOLBAR)
        btnRestore.set_property("tooltip-text", "Restore backup")
        btnRestore.connect("clicked", self.restoreBackup)
        
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL, margin=12)
        btnBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        btnBox.add(btnImport)
        btnBox.add(btnExport)
        btnBox.add(btnRestore)
        
        popoverBox.add(btnBox)
        self.menuPopover.add(popoverBox)
        
        btnbox = Gtk.ButtonBox()
        btnbox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        Gtk.StyleContext.add_class(btnbox.get_style_context(), "linked")

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="list-add-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.onAdd)
        btnbox.add(button)

        button = Gtk.ToggleButton()
        icon = Gio.ThemedIcon(name="document-edit-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.onEditMode)
        btnbox.add(button)
        
        hb.pack_start(btnbox)

        # contents

        self.box_outer = Gtk.ScrolledWindow()
        self.box_outer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(self.box_outer)
        self.listbox = Gtk.ListBox(margin=0)
        self.listbox.connect("row-activated", self.onRowActivated)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.box_outer.add(self.listbox)

    def onAdd(self, widget):
        editDialog = EditDialog(self, self.confFile)
        editDialog.run()
        editDialog.destroy()
        self.populate(self.isWayland)

    def onEditMode(self, button):
        self.editMode = button.get_active()
        self.populate(self.isWayland)

    def onEdit(self, widget, i):
        editDialog = EditDialog(self, self.confFile, i)
        editDialog.run()
        editDialog.destroy()
        self.populate(self.isWayland)
    
    def onEditFile(self, widget):
        dialog = UnsupportedLinesDialog(self, self.confFile)
        dialog.run()
        dialog.destroy()

    def onEditFileExternal(self, widget):
        self.hide()
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK_CANCEL, "Opening file in default text editor")
        dialog.format_secondary_text(
            "As Gestures doesn't support real-time file updates yet, external modifications need to be done while Gestures is closed. Would you still like to proceed?")
        dialog.set_modal(True)
        
        if(dialog.run()  == Gtk.ResponseType.OK):
            dialog.destroy()
            call(["xdg-open", self.confFile.filePath])
            sys.exit(0)
        else:
            dialog.destroy()
            self.show()
        
    
    def onAbout(self, widget):
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        authors = ["Raffaele T. (cunidev)"]
        
        about_dialog.set_program_name("Gestures")
        about_dialog.set_comments("A minimal, modern Gtk+ app for Linux touchpad gestures, based on the popular libinput-gestures tool.")
        about_dialog.set_version(__version__)
        
        try:
            about_dialog.set_logo(Gtk.IconTheme.get_default().load_icon("org.cunidev.gestures", 128, 0))
        except:
            pass
        
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.set_authors(authors)
        about_dialog.set_website("https://gitlab.com/cunidev/gestures")
        about_dialog.set_website_label("cunidev's GitLab")
        about_dialog.set_title("")
        
        about_dialog.show()
        
    def onRowActivated(self, widget, i):
        if(len(self.confFile.gestures) > 0):
            command = self.confFile.gestures[i.get_index()].command
            print("Executing command: " + command)
            try:
                Popen(shlex.split(command))
            except:
                print("Can't execute command!")
            
    def importFile(self, button):
        dialog = Gtk.FileChooserDialog("Import profile", self, Gtk.FileChooserAction.OPEN, 
                                                  (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_current_folder(expanduser("~"))
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        filter = Gtk.FileFilter() 
        filter.set_name(".conf files") 
        filter.add_pattern("*.conf")
        dialog.add_filter(filter)
        
        filter = Gtk.FileFilter()
        filter.set_name("All files") 
        filter.add_pattern("*")
        dialog.add_filter(filter) 
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            dialog.destroy()
            
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK_CANCEL, "Overwrite current profile?")
            dialog.format_secondary_text("This operation can't be undone. Make sure you export your current profile first!")
            if(dialog.run() == Gtk.ResponseType.OK):
                if(self.confFile.importFile(path)):
                    dialog.destroy()
                    dialog = Gtk.MessageDialog(
                        self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Profile imported")
                    dialog.format_secondary_text(
                        "Please re-open Gestures for changes to take effect")
                    dialog.set_modal(True)
                    dialog.run()
                    dialog.destroy()
                    sys.exit(0)
                else:
                    dialog.destroy()
                    dialog = Gtk.MessageDialog(
                        self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't import profile")
                    dialog.format_secondary_text(
                        "Please check permissions")
                    dialog.set_modal(True)
                    dialog.run()
                    dialog.destroy()
            else:
                    dialog.destroy()
            
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        
    def exportFile(self, button):
        dialog = Gtk.FileChooserDialog("Save as", self, Gtk.FileChooserAction.SAVE, 
                                                  (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                    Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name("Gestures.conf")
        dialog.set_current_folder(expanduser("~"))
        dialog.set_default_response(Gtk.ResponseType.OK) 
        dialog.set_do_overwrite_confirmation(True)
        
        filter = Gtk.FileFilter() 
        filter.set_name(".conf files") 
        filter.add_pattern("*.conf")
        dialog.add_filter(filter)
        
        filter = Gtk.FileFilter()
        filter.set_name("All files") 
        filter.add_pattern("*")
        dialog.add_filter(filter) 
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            if(self.confFile.exportFile(path)):
                dialog.destroy()
                dialog = Gtk.MessageDialog(
                    self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Profile exported")
                dialog.format_secondary_text(
                    "You can find it at "+path)
                dialog.set_modal(True)
                dialog.run()
                dialog.destroy()
            else:
                dialog.destroy()
                dialog = Gtk.MessageDialog(
                    self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't export profile")
                dialog.format_secondary_text(
                    "Please check permissions for selected folder")
                dialog.set_modal(True)
                dialog.run()
                dialog.destroy()
            
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
    
    def restoreBackup(self, button):
        self.hide()
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK_CANCEL, "Restore backup configuration?")
        dialog.format_secondary_text(
            "This operation can't be undone. The app will be closed after restoring, and all changes will be lost.")
        if(dialog.run() == Gtk.ResponseType.OK):
            if(self.confFile.restore()):

                dialog.destroy()
                dialog = Gtk.MessageDialog(
                    self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Backup file restored.")
                dialog.format_secondary_text(
                    "Gestures will be closed. Please remember that re-opening this app will result in overwriting the configuration file.")
                dialog.set_modal(True)
                dialog.run()
                dialog.destroy()
                sys.exit(0)
            else:
                dialog.destroy()
                dialog = Gtk.MessageDialog(
                    self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't restore backup file.")
                dialog.format_secondary_text("The file might not exist.")
                dialog.set_modal(True)
                dialog.run()
                dialog.destroy()
                self.show()
        else:
            dialog.destroy()
            self.show()

    def onDelete(self, widget, i):
        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK_CANCEL, "Confirm deletion?")
        dialog.format_secondary_text("This operation can't be undone.")
        if(dialog.run() == Gtk.ResponseType.OK):
            del self.confFile.gestures[i]
            self.confFile.save()

            try:
                self.confFile.reloadProcess()
            except:
                err = ErrorDialog(self)
                err.showNotInstalledError(self)

        dialog.destroy()
        self.populate(self.isWayland)

    def showMenu(self, widget):
        if self.menuPopover.get_visible():
            self.menuPopover.popdown()
        else:
            self.menuPopover.popup()
            self.menuPopover.show_all()

    def setConfFile(self, confFile):
        self.confFile = confFile
        
    def populate(self, isWayland = False):
        # redraw

        for child in self.listbox.get_children():
            child.destroy()

        if(len(self.confFile.gestures) == 0):
            label = Gtk.Label()
            label.set_markup("<big><big>No gestures.</big></big>")
            box = Gtk.ListBoxRow(margin=150)
            box.add(label)
            self.listbox.add(box)

            # TODO: fix (ugly and temporary!)

        for i, gesture in enumerate(self.confFile.gestures):

            row = Gtk.ListBoxRow(margin=0)
            
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15, margin = 20)
            row.add(hbox)
            
            if(isWayland and "xdotool" in gesture.command):
                icon = Gtk.Image.new_from_icon_name("action-unavailable", Gtk.IconSize.LARGE_TOOLBAR)
                icon.set_pixel_size(80)
                hbox.set_property("tooltip-text", "xdotool not available in Wayland")
                hbox.pack_start(icon, False, False, 10)
            else:
                icon = Gtk.Image.new_from_icon_name("input-touchpad", Gtk.IconSize.LARGE_TOOLBAR)
                icon.set_pixel_size(80)
                hbox.pack_start(icon, False, False, 10)
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.props.valign = Gtk.Align.CENTER

            hbox.pack_start(vbox, True, True, 0)

            label = Gtk.Label(xalign=0)
            label.set_markup("<b>" + str(gesture.fingers) + "-finger " + gesture.type + " " + gesture.direction +
                              "</b>")
            vbox.pack_start(label, False, True, 0)

            if len(gesture.command) > 74:
                cmd = gesture.command[:70] + "..."
            else:
                cmd = gesture.command
            
            box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            icon = Gtk.Image.new_from_icon_name("utilities-terminal-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
            label = Gtk.Label("  " + cmd, xalign=0)
            box2.add(icon)
            box2.add(label)
            
            vbox.pack_start(box2, False, True, 0)

            if(self.editMode):
                deleteButton = Gtk.Button()
                icon = Gio.ThemedIcon(name="edit-delete-symbolic")
                image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
                deleteButton.add(image)

                editButton = Gtk.Button()
                icon = Gio.ThemedIcon(name="document-edit-symbolic")
                image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
                editButton.add(image)

                editButton.connect("clicked", self.onEdit, i)

                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                box.props.valign = Gtk.Align.CENTER
                Gtk.StyleContext.add_class(box.get_style_context(), "linked")
                
                box.add(editButton)
                box.add(deleteButton)

                deleteButton.connect("clicked", self.onDelete, i)

                hbox.pack_start(box, False, True, 10)
            else:
                switch = Gtk.Switch()
                switch.props.active = gesture.enabled
                switch.props.valign = Gtk.Align.CENTER
                hbox.pack_start(switch, False, True, 10)
                switch.connect("state-set", self.setActive, i)

            self.listbox.add(row)

        self.listbox.show_all()

    def setActive(self, widget, enabled, i):
        self.confFile.gestures[i].enabled = enabled
        self.confFile.save()
        try:
            self.confFile.reloadProcess()
        except:
            err = ErrorDialog(self)
            err.showNotInstalledError(self)
            
    def showNotInstalledError(self,win):
        dialog = Gtk.MessageDialog(
                win, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't load libinput-gestures")
        dialog.format_secondary_text(
            "Make sure it is correctly installed. The configuration file has been saved anyway.")
        dialog.run()
        dialog.destroy()


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
        
        try:
            confFile = ConfigFileHandler(expanduser("~"), __version__)
            if(confFile.createFileIfNotExisting()):
                print("INFO: An empty configuration file has been successfully generated")
        
            confFile.openFile()
            if not(confFile.isValid()):
                if (confFile.backup()):
                    dialog = Gtk.MessageDialog(win, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                               "The current configuration file hasn't been created with this tool.")
                    dialog.format_secondary_text("The old file has been backed up to " + confFile.backupPath +
                                                 ", its contents will be extracted and the conf file has been overridden.")
                    dialog.run()
                    dialog.destroy()
                    confFile.save()
                else:
                    dialog = Gtk.MessageDialog(
                        win, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Invalid configuration file, can't backup!")
                    dialog.format_secondary_text(
                        "Can't create backup file! For security reasons, this tool can't be run.")
                    dialog.run()
                    dialog.destroy()
                    sys.exit(-1)
            else:
                pass
        
        except:
            dialog = Gtk.MessageDialog(
                win, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't open configuration file.")
            dialog.format_secondary_text(
                "The configuration file can't be opened or created, check permissions.")
            dialog.run()
            dialog.destroy()
            sys.exit(-1)
    
        # load file
        win.setConfFile(confFile)
        win.set_default_size(800, 500)
        win.populate(isWayland)
        
        try:
            confFile.reloadProcess()
        except:
            err = ErrorDialog(win)
            err.showNotInstalledError(win)
            
        win.show_all()
    
    
    
