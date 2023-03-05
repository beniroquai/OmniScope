#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:30:11 2022

@author: bene
"""
import socket
from datetime import datetime
net = "192.168.2.1"  # input("Enter the IP address: ")
net1 = net.split('.')
a = '.'

net2 net1[0] + a + net1[1] + a + net1[2] + a
st1 = 2  # int(input("Enter the Starting Number: "))
en1 = 255  # int(input("Enter the Last Number: "))
en1 = en1 + 1
t1 = datetime.now()


def scan(addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(1)
    result = s.connect_ex((addr, 135))
    if result == 0:
        return 1
    else:
        return 0


def run1():
    for ip in range(st1, en1):
        addr = net2 + str(ip)

        if (scan(addr)):
            print(addr, "is live")
        else:
            print(addr, "is not live")


run1()
t2 = datetime.now()
total = t2 - t1
print("Scanning completed in: ", total)


#%%
import requests
allScopes = []


import numpy as np
import threading
import time


# Define a function for the thread
def findOmniscope(baseURL="", ipRange=(0,50),endpoint="/getID"):
    print("searching in range: "+str(ipRange))
    for ip in range(*ipRange):
       URL = baseURL+str(ip)+endpoint
       try:
           source = requests.get(URL,timeout=0.5)
           print(URL)
           allScopes.append(URL)
       except :
           pass
       
# Create two threads as follows
baseURL="http://192.168.2."
endpoint="/getID"


nThreads = 20

for iThread in range(np.int32(np.ceil(255/nThreads))):
    threading.Thread(target=findOmniscope, args=(baseURL, (nThreads*iThread,iThread*nThreads+nThreads), "/getID")).start()
    