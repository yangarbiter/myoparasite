#! /usr/bin/env python2
from __future__ import print_function
import json
import numpy as np
import os
import random
import struct
import subprocess
import sys
import tempfile
import threading
import time

import Classifier

buf = ""

class readdataThread (threading.Thread) :
    def __init__ (self, FILE) :
        super (readdataThread, self).__init__ ()
        self.FILE = FILE
    def run (self) :
        global buf

        while True :
            buf += self.FILE.read (50 * 4)

def extract_feature (data1, data2):
    return np.concatenate((
            (np.absolute(np.fft.fft(data1))) ,
            (np.absolute(np.fft.fft(data2))) ) ).tolist()

def getdata (raw) :
    data1 = []
    data2 = []
    m = 1
    for j in range (0, len (raw), 2) :
        n = struct.unpack ("<h", raw[j:j+2])[0]
        if m == 1 :
            data1.append (float(n))
            m = 2
        else :
            data2.append (float(n))
            m = 1
    return data1, data2

def record (data_file, output) :
    labels = range(Classifier.NUM_OF_LABELS-1, -1, -1) * 15
    # random.shuffle(labels)
    datas = []
    rawdata1 = []
    rawdata2 = []

    record_time = len (labels)
    tmp_fd, tmp_file = tempfile.mkstemp()
    shcmd = "arecord -c 2 -d {} -t raw -r 2000 -f S16_LE - 2>/dev/null >{}"\
        .format(record_time + 1, tmp_file)
    proc = subprocess.Popen (shcmd , stdout = subprocess.PIPE, shell = True)
    for i in range (-1, record_time) :
        if i > -1 :
            output (labels[i])
        time.sleep (1)

    f = os.fdopen (tmp_fd)
    for i in range (-1, record_time) :
        if i == -1 :
            f.read (2000 * 4)
            continue
        data1, data2 = getdata (f.read (2000 * 4))

        rawdata1.append(data1)
        rawdata2.append(data2)
    f.close()
    os.unlink(tmp_file)

    f = open (data_file, "w")
    f.write (json.dumps (zip(labels, rawdata1, rawdata2)))
    f.close ()

    return rawdata1, rawdata2, labels


def readdata(data_file):
    with open(data_file, "r") as f:
        y, X1, X2 = zip(*json.loads(f.readline()))
    Classifier.NUM_OF_LABELS = len (set (y))
    return X1, X2, y


def train(rawdata1, rawdata2, y, info):
    info ("start training")
    X = []
    X1 = rawdata1
    X2 = rawdata2
    y_2 = []
    for yi, x1, x2 in zip(y, X1, X2):
        for i in range(500, 1500, Classifier.WINDOW_SHIFT_TRAIN):
            X.append( extract_feature(
                        x1[i: i+Classifier.WINDOW_SIZE],
                        x2[i: i+Classifier.WINDOW_SIZE]) )
            y_2.append( yi )
    y = y_2
    scalers, classifiers, scores = Classifier.gen_model(X, y, verbose=False)
    info ("finish training")
    return scalers, classifiers, scores


def predict (scalers, classifiers, scores, info, output) :
    global buf

    info ("start predict")

    shcmd = "arecord -t raw -c 2 -r 2000 -f S16_LE - 2>/dev/null"
    proc = subprocess.Popen (shcmd, stdout = subprocess.PIPE, shell = True)
    read_thread = readdataThread (proc.stdout)
    read_thread.daemon = True
    read_thread.start ()

    count = 0
    p = [0] * Classifier.NUM_OF_LABELS
    while True :
        if len (buf) >= Classifier.WINDOW_SIZE * 4 :
            data1, data2 = getdata (buf[-Classifier.WINDOW_SIZE * 4:])
            buf = buf[-(Classifier.WINDOW_SIZE - 50) * 4:]

            X = extract_feature(data1, data2)
            tp = Classifier.multi_classification([X], scalers, classifiers, scores)[0]

            p[tp] += 1
            count += 1
            if count >= 5 :
                maj = p.index (max (p))
                count = 0
                p = [0] * Classifier.NUM_OF_LABELS
                output (maj)
                sys.stdout.flush ()

    read_thread.join ()


def message (msg):
    sys.stderr.write(msg + '\n')

def main () :
    argv = sys.argv
    argc = len (argv)
    if argc != 2 :
        sys.stderr.write ("Usage: %s {new|read}\n" % (argv[0]))
        exit (1)

    Classifier.NUM_OF_LABELS = 2
    if argv[1] == "new" :
        rawx1, rawx2, y = record('rawdata', print)
    elif argv[1] == "read" :
        rawx1, rawx2, y = readdata('rawdata')
    else :
        sys.stderr.write ("Wrong arguments\n")
        exit (1)
    scalers, classifiers, scores = train (rawx1, rawx2, y, message)
    predict (scalers, classifiers, scores, message, print)

if __name__ == "__main__" :
    main ()
