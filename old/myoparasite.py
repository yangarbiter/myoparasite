#! /usr/bin/env python2

from mouse_action import mouse_action
import record
import subprocess


def main () :
    predict_proc = subprocess.Popen (["./record.py", "read"], stdout = subprocess.PIPE)
    mouse_proc = subprocess.Popen (["nc", "192.168.247.2", "5555"], stdout = subprocess.PIPE, stdin = subprocess.PIPE)

    import time

    while True :
        predict = int (predict_proc.stdout.readline ())
        mouse_proc.stdin.write ('\n')
        mouse_proc.stdin.flush ()
        mouse_proc.stdout.read (10000)
        mouse = int (mouse_proc.stdout.readline ())
        print (predict, mouse)
        if predict and mouse :
            mouse_action (mouse)
    

if __name__ == "__main__" :
    main ()
