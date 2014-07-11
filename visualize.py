#! /usr/bin/env python2
import json
import matplotlib.pyplot as plt
import sys
import numpy as np

argv = sys.argv
argc = len (argv)

if argc != 2 :
    print ("Usage : %s [data]" % (argv[0]))
    exit (1)

f = open (argv[1], "r")
labels, datas1, datas2 = zip(*json.loads (f.readline ()))
for i in range (0, len (datas1)) :
    print (labels[i])
    plt.subplot (2, 1, 1)
    plt.plot (datas1[i])
    plt.subplot (2, 1, 2)
    plt.plot (datas2[i])
    plt.show ()
f.close ()
