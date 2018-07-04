import os
from setuptools import setup
from gestures.__version__ import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "gestures",
    version = __version__,
    author = "Raffaele T.",
    author_email = "raffaele@board-db.org",
    description = ("Minimal Gtk+ app for libinput-gestures"),
    license = "GPL-3.0",
    url = "https://gitlab.com/cunidev/gestures",
    packages=['gestures'],
    scripts = ['data/gestures'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    package_data    = {'gestures': ['data/style.css']},
    data_files      = [("/usr/share/applications", ["data/org.cunidev.gestures.desktop"]),
                       ("/usr/share/metainfo", ["data/org.cunidev.gestures.appdata.xml"]),
                       ("/usr/share/icons/hicolor/scalable/apps/", ["data/org.cunidev.gestures.svg"])]
)
