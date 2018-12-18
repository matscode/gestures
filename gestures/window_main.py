import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Pango

import shlex
from shlex import split
from sys import exit
from subprocess import Popen, call
from os.path import expanduser
from os import getenv
from gestures.configfile import ConfigFileHandler
from gestures.gesture import Gesture
from gestures.__version__ import __version__

from .dialog_preferences import PreferencesDialog, UnsupportedLinesDialog
from .dialog_error import ErrorDialog
from .dialog_edit import EditDialog
from .dialog_about import AppAboutDialog

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

        self.set_titlebar(hb)
        
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="open-menu-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        hb.pack_end(button)
        button.connect("clicked", self.showMenu)

        self.menuPopover = Gtk.Popover.new(button)
        self.menuPopover.set_size_request(250, 100)
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=5)

        # upper toolbar
        btnImport = Gtk.Button.new_from_icon_name("document-open", Gtk.IconSize.LARGE_TOOLBAR)
        btnImport.set_property("tooltip-text", "Import")
        btnImport.connect("clicked", self.importFile)
        
        btnExport = Gtk.Button.new_from_icon_name("document-save", Gtk.IconSize.LARGE_TOOLBAR)
        btnExport.set_property("tooltip-text", "Export")
        btnExport.connect("clicked", self.exportFile)
        
        btnRestore = Gtk.Button.new_from_icon_name("document-revert", Gtk.IconSize.LARGE_TOOLBAR)
        btnRestore.set_property("tooltip-text", "Restore backup")
        btnRestore.connect("clicked", self.restoreBackup)
        
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        btnBox.set_layout(Gtk.ButtonBoxStyle.EXPAND)
        btnBox.add(btnImport)
        btnBox.add(btnExport)
        btnBox.add(btnRestore)
        
        popoverBox.add(btnBox)

        # other buttons - TODO: make Gio.Menu
        
        separator = Gtk.Separator()
        popoverBox.add(separator)

        button = Gtk.Button("Edit unsupported")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onEditFile)
        #popoverBox.add(button)

        button = Gtk.Button("Edit manually")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onEditFileExternal)
        popoverBox.add(button)

        button = Gtk.Button("Preferences")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.openSettings)
        popoverBox.add(button)

        button = Gtk.Button("About")
        Gtk.StyleContext.add_class(button.get_style_context(), "flat")
        button.connect("clicked", self.onAbout)
        popoverBox.add(button)

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

    def initialize(self):
        try:
            confFile = ConfigFileHandler(expanduser("~"), __version__)
            if(confFile.createFileIfNotExisting()):
                print("INFO: An empty configuration file has been successfully generated")

            confFile.openFile()
            if not(confFile.isValid()):
                if (confFile.backup()):
                    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK,
                                               "The current configuration file hasn't been created with this tool.")
                    dialog.format_secondary_text("The old file has been backed up to " + confFile.backupPath +
                                                 ", its contents will be extracted and the conf file has been overridden.")
                    dialog.run()
                    dialog.destroy()
                    confFile.save()
                else:
                    dialog = Gtk.MessageDialog(
                        self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Invalid configuration file, can't backup!")
                    dialog.format_secondary_text(
                        "Can't create backup file! For security reasons, this tool can't be run.")
                    dialog.run()
                    dialog.destroy()
                    exit(-1)
            else:
                pass

        except:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Can't open configuration file.")
            dialog.format_secondary_text(
                "The configuration file can't be opened or created, check permissions.")
            dialog.run()
            dialog.destroy()
            exit(-1)

        # load file
        self.setConfFile(confFile)
        self.set_default_size(600, 400)
        self.populate(self.isWayland)

        try:
            confFile.reloadProcess()
        except:
            err = ErrorDialog(self)
            err.showNotInstalledError(self)

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
            exit(0)
        else:
            dialog.destroy()
            self.show()
        
    def openSettings(self, widget):
        dialog = PreferencesDialog(self, self.confFile)
        dialog.run()
        dialog.destroy()

    def onAbout(self, widget):
        about_dialog = AppAboutDialog(self)
        about_dialog.run()
        about_dialog.destroy()
        
    def onRowActivated(self, widget, i):
        if(len(self.confFile.gestures) > 0):
            command = self.confFile.gestures[i.get_index()].command
            print("Executing command: " + command)
            try:
                Popen(split(command))
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
                    self.initialize()
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

                # dialogs are annoying
                #dialog = Gtk.MessageDialog(
                #    self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Profile exported")
                #dialog.format_secondary_text(
                #    "You can find it at "+path)
                #dialog.set_modal(True)
                #dialog.run()
                #dialog.destroy()
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
                    "Gestures will be closed. Please remember that re-opening this app might result in overwriting the current backup file.")
                dialog.set_modal(True)
                dialog.run()
                dialog.destroy()
                exit(0)
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
            
            icon = Gtk.Image.new_from_icon_name("input-touchpad", Gtk.IconSize.LARGE_TOOLBAR)
            icon.set_pixel_size(80)
            hbox.pack_start(icon, False, False, 10)
            
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.props.valign = Gtk.Align.CENTER

            hbox.pack_start(vbox, True, True, 0)

            hbox.pack_end(vbox, True, True, 0)

            label = Gtk.Label(xalign=0)
            label.set_markup("<b>" + str(gesture.fingers) + "-finger " + gesture.type + " " + gesture.direction +
                              "</b>")
            vbox.pack_start(label, False, True, 0)
            
            box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            icon = Gtk.Image.new_from_icon_name("utilities-terminal-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
            label = Gtk.Label("  " + gesture.command, xalign=0)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            box2.add(icon)
            box2.add(label)
            
            vbox.pack_start(box2, False, True, 0)

            if(isWayland and "xdotool" in gesture.command):
                box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                icon = Gtk.Image.new_from_icon_name("dialog-warning", Gtk.IconSize.SMALL_TOOLBAR)
                label = Gtk.Label(xalign=0)
                label.set_markup(" <span color='darkred'><i><small>Unsupported on Wayland sessions.</small></i></span>")
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
