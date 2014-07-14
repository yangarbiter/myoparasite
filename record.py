#! /usr/bin/env python
import fcntl
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import subprocess
import sys
import time
import threading
import struct

import Classifier 
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

import code

#scaler1 = StandardScaler()
#scaler2 = StandardScaler()
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


def record () :
    labels = range(Classifier.NUM_OF_LABELS-1, -1, -1) * 15
    # random.shuffle(labels)
    datas = []
    rawdata1 = []
    rawdata2 = []

    record_time = len (labels)
    shcmd = "arecord -c 2 -d %d -t raw -r 2000 -f S16_LE - 2>/dev/null > tmppp" % (record_time + 1)
    proc = subprocess.Popen (shcmd , stdout = subprocess.PIPE, shell = True)
    for i in range (-1, record_time) :
        if i > -1 :
            print (labels[i])
        time.sleep (1)

    f = open ('tmppp', 'r')
    for i in range (-1, record_time) :
        if i == -1 :
            f.read (2000 * 4)
            continue
        data1, data2 = getdata (f.read (2000 * 4))
        # plt.subplot(2,1,1)
        # plt.plot(data1)
        # plt.subplot(2,1,2)
        # plt.plot(data2)
        # plt.show()

        rawdata1.append(data1)
        rawdata2.append(data2)

    f = open ("rawdata", "w")
    f.write (json.dumps (zip(labels, rawdata1, rawdata2)))
    f.close ()

    return rawdata1, rawdata2, labels


def readdata():
    with open("rawdata", "r") as f:
        y, X1, X2 = zip(*json.loads(f.readline()))
    Classifier.NUM_OF_LABELS = len (set (y))
    return X1, X2, y


def train(rawdata1, rawdata2, y):
    sys.stderr.write ("start training\n")
    X = []
    X1 = rawdata1
    X2 = rawdata2
    y_2 = []
    for yi, x1, x2 in zip(y, X1, X2):
        for i in range(500, 1500, Classifier.WINDOW_SHIFT_TRAIN):
            X.append( extract_feature(
                        x1[i: i+Classifier.WINDOW_SIZE],
                        x2[i: i+Classifier.WINDOW_SIZE]) )
        #    X.append(x1[i: i+Classifier.WINDOW_SIZE])
            # X.append( np.concatenate(( 
            #         np.absolute(np.fft.fft(x1[i: i+Classifier.WINDOW_SIZE])) , 
            #         np.absolute(np.fft.fft(x2[i: i+Classifier.WINDOW_SIZE])) ) ).tolist())
            y_2.append( yi )
    y = y_2
    scalers, classifiers, scores = Classifier.gen_model(X, y, verbose=False)
    """
    scalers = []
    classifiers = KNeighborsClassifier(n_neighbors=1).fit(X, y)
    scores = []
    """
    sys.stderr.write ("finish training\n")
    return scalers, classifiers, scores


def predict (scalers, classifiers, scores) :
    global buf

    sys.stderr.write ("start predict\n")

    shcmd = "arecord -t raw -c 2 -r 2000 -f S16_LE - 2>/dev/null"
    proc = subprocess.Popen (shcmd, stdout = subprocess.PIPE, shell = True)
    read_thread = readdataThread (proc.stdout)
    read_thread.start ()
    
    count = 0
    p = [0] * Classifier.NUM_OF_LABELS
    while True :
        if len (buf) >= Classifier.WINDOW_SIZE * 4 :
            data1, data2 = getdata (buf[-Classifier.WINDOW_SIZE * 4:])
            buf = buf[-(Classifier.WINDOW_SIZE - 50) * 4:]

            X = extract_feature(data1, data2)
            #tp = classifiers.predict([X])[0]
            tp = Classifier.multi_classification([X], scalers, classifiers, scores)[0]

            p[tp] += 1
            count += 1
            if count >= 5 :
                maj = p.index (max (p))
                count = 0
                p = [0] * Classifier.NUM_OF_LABELS
                print (maj)
                sys.stdout.flush ()

    
    
    read_thread.join ()


def main () :
    argv = sys.argv
    argc = len (argv)
    if argc != 2 :
        sys.stderr.write ("Usage: %s {new|read}\n" % (argv[0]))
        exit (1)

    if argv[1] == "new" :
        Classifier.NUM_OF_LABELS = 2
        rawx1, rawx2, y = record()
    elif argv[1] == "read" :
        rawx1, rawx2, y = readdata()
    else :
        sys.stderr.write ("Wrong arguments\n")
        exit (1)
    scalers, classifiers, scores = train (rawx1, rawx2, y)
    """
    for i, j in zip(rawx1[:-1], rawx2[:-1]):
        print Classifier.multi_classification(extract_feature(i[500:1000], j[500:1000])[:500], scalers, classifiers, scores)
    """
    predict (scalers, classifiers, scores)

if __name__ == "__main__" :
    main ()
