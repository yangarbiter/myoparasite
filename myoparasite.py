#! /usr/bin/env python2

from mouse_action import mouse_action
import record
import subprocess


def main () :
    predict_proc = subprocess.Popen (["./record.py", "read"], stdout = subprocess.PIPE)
    mouse_proc = subprocess.Popen (["nc", "192.168.247.2", "5555"], stdout = subprocess.PIPE)

    import time

    while True :
        predict_proc.stdout.flush ()
        predict = int (predict_proc.stdout.readline ())
        mouse_proc.stdout.flush ()
        mouse = int (mouse_proc.stdout.readline ())
        print (predict, mouse)
        if predict == 1 :
            pass
            mouse_action (mouse)
    

if __name__ == "__main__" :
    main ()
