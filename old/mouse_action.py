#!/usr/bin/env python2

from ctypes import *

libxdo = None
xdo_handle = None
xdo_func_new = None
xdo_func_mouse_move = None
xdo_func_mouse_click = None

class xdo_t(Structure):
    pass

def init_libxdo():
    global libxdo
    global xdo_func_new
    global xdo_func_mouse_move
    global xdo_func_mouse_click

    try:
        libxdo = cdll.LoadLibrary('libxdo.so.3')
        xdo_func_new = getattr(libxdo, 'xdo_new')
        xdo_func_mouse_move = getattr(libxdo, 'xdo_move_mouse_relative')
        xdo_func_mouse_click = getattr(libxdo, 'xdo_click_window')
        return True
    except OSError:
        pass

    try:
        libxdo = cdll.LoadLibrary('libxdo.so.2')
        xdo_func_new = getattr(libxdo, 'xdo_new')
        xdo_func_mouse_move = getattr(libxdo, 'xdo_mousemove_relative')
        xdo_func_mouse_click = getattr(libxdo, 'xdo_click')
        return True
    except OSError:
        pass

    return False


def init_func_args():
    xdo_func_new.argtypes = [c_char_p]
    xdo_func_new.restype = POINTER(xdo_t)
    xdo_func_mouse_move.argtypes = [POINTER(xdo_t), c_int, c_int]
    xdo_func_mouse_move.restype = c_int
    xdo_func_mouse_click.argtypes = [POINTER(xdo_t), c_long, c_int]
    xdo_func_mouse_click.restype = c_int

def init_xdo_handle():
    global xdo_handle
    xdo_handle = xdo_func_new(None)
    if xdo_handle == None:
        return False
    return True

def mouse_action(action):
    if libxdo == None:
        if not init_libxdo():
            raise 'Cannot load library: libxdo'
        else:
            init_func_args()

    if xdo_handle == None:
        if not init_xdo_handle():
            raise 'Cannot create object: xdo_t'

    if action >= 1 and action <= 5:
        xdo_func_mouse_click(xdo_handle, 0, action)


if __name__ == '__main__':
    import sys
    mouse_action(int(sys.argv[1]))
