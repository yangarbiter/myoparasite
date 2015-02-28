#! /usr/bin/env python2
from __future__ import print_function
from gi.repository import Gtk, GdkPixbuf, GLib
from threading import Thread
from Queue import Queue
import sys

import record

record.Classifier.NUM_OF_LABELS = 2


finger_file_map = [
    'images/right-thumb.svg',
    'images/right-index-finger.svg',
    'images/right-middle-finger.svg',
    'images/right-ring-finger.svg',
    'images/right-little-finger.svg'
]

finger_obj_map = []

NAME = 'myoparasite'
FUNCTION_NEW = 1
FUNCTION_READ = 2


Gtk.init(sys.argv)

function = Gtk.Dialog(title='Please choose a function')
function.connect('delete-event', Gtk.main_quit)
function.add_button('New', FUNCTION_NEW)
function.add_button('Read', FUNCTION_READ)
function.show_all()
f = function.run()
if f == Gtk.ResponseType.DELETE_EVENT:
	exit(0)
function.destroy()

for finger_file in finger_file_map:
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(finger_file)
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
        finger_file, pixbuf.get_width() * 4, pixbuf.get_height() * 4)
    finger_obj_map.append(pixbuf)

def set_status(msg):
    print(msg)
    ui_queue.put(('status', msg))

def set_image(msg):
    print(msg)
    num = int(msg)
    ui_queue.put(('image', msg))

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=NAME)
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(5)
        self.grid.set_column_homogeneous(True)
        self.add(self.grid)

        self.status = Gtk.Label('status')
        self.grid.attach(self.status, 0, 0, 1, 1)
        self.image = Gtk.Image()
        self.grid.attach(self.image, 0, 1, 1, 1)
        self.spinner = Gtk.Spinner()
        self.grid.attach(self.spinner, 0, 2, 1, 1)

        self.show_all()
        self.spinner.hide()


def start_work(function):
    if function == FUNCTION_NEW:
        rawx1, rawx2, y = record.record('rawdata', set_image)
    elif function == FUNCTION_READ:
        rawx1, rawx2, y = record.readdata('rawdata')

    ui_queue.put(('spinner', True))
    scalers, classifiers, scores = record.train (
        rawx1, rawx2, y, set_status)
    ui_queue.put(('spinner', False))
    record.predict (
        scalers, classifiers, scores, set_status, set_image)

def update_ui(unused=None):
    while not ui_queue.empty():
        task = ui_queue.get()
        if task[0] == 'status':
            main.status.set_text(task[1])
        elif task[0] == 'image':
            main.image.set_from_pixbuf(finger_obj_map[task[1]])
        elif task[0] == 'spinner':
            if task[1]:
                main.spinner.show()
                main.spinner.start()
            else:
                main.spinner.hide()
                main.spinner.stop()

    GLib.timeout_add(100, update_ui, None)


ui_queue = Queue()

work = Thread(target=start_work, args=(f,))
work.daemon = True
work.start()

main = MainWindow()
main.set_border_width(10)
main.connect('delete-event', Gtk.main_quit)
GLib.timeout_add(100, update_ui, None)
Gtk.main()
exit(0)
