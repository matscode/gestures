*Not* a definitive thing, but rather a bunch of ideas for next versions

0.1.3
* [x]  logo

0.1.4
* [x]  export/import

0.2.0
* [x] new lines support
* [x] click to execute
* [x]  gui redesign

0.2.1
* [x] open in external editor


0.2.0
* [x] echo Useless > notify-send "Command performed"
* [x] warning that wmctrl and xdotool won't work (w/ Don't show anymore) when running on wayland

0.2.1
* [x] settings window (for swipe_threshold)

0.2.x
* [ ] i18n, meson (Bilal)
* [ ] better warning for Wayland unsupported commands w/ Learn more link
* [x] code cleanup
* [ ] maybe: textarea to edit unsupported lines (where to implement in GUI?)
* [ ] popup error if can't start libinput gestures
* [ ] get version for libinput-gestures at boot, warn if unsupported (w/ Don't show anymore)

0.3.x
* [ ]  no need for reboot on file import/export (+inotify if external edit detected)
* [ ]  nohup wrapper support (checkbox for Run as app or something)
* [ ]  multi profiles
* [ ]  xdotool gui (keypress → xdotool command) (small keyboard icon near Command field perhaps?)
* [ ] app chooser (?)

0.4.x
* [ ] animations
* [ ] dbus gui/helper?