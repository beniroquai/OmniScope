#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 22:35:33 2022

@author: bene
"""


import cv2
import urllib.request
import numpy as np

stream = urllib.request.urlopen('http://192.168.43.203/cam.mjpeg')
bytes = bytes()
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('i', i)
        if cv2.waitKey(1) == 27:
            exit(0)
            
            
#%%

import cv2
url = "http://192.168.178.38:81/stream.mjpeg"
cap = cv2.VideoCapture(url)

while True:
  ret, frame = cap.read()
  cv2.imshow('Video', frame)

  if cv2.waitKey(1) == 27:
    exit(0)
    
#%%

import urllib
import cv2
import numpy as np
import matplotlib.pyplot as plt

def displayJPEG(name="CAM1", url=""):
    while True:
        imgResp=urllib.request.urlopen(url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)
    
        # all the opencv processing is done here
        plt.title(name), plt.imshow(img), plt.show()
        #if ord('q')==cv2.waitKey(10):
        #    exit(0)
        
#%
allScopes = ['http://192.168.2.164/cam-lo.jpg',
 'http://192.168.2.163/cam-lo.jpg',
 'http://192.168.2.165/cam-lo.jpg',
 'http://192.168.2.166/cam-lo.jpg']

import threading 

name = "CAM"
iterator = 0
for url in allScopes:
    print("Starint:"+url)
    threading.Thread(target=displayJPEG, args=(name+str(iterator), url)).start()
    iterator+=1
    
#%%
import cv2
import urllib.request
import numpy as np



url = "http://192.168.2.171"
url = "http://192.168.178.47"
stream = urllib.request.urlopen(url+":81/stream.mjpeg")
bytesJPEG = bytes()
while True:
    bytesJPEG += stream.read(512)
    a = bytesJPEG.find(b'\xff\xd8')
    b = bytesJPEG.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytesJPEG[a:b+2]
        bytesJPEG = bytesJPEG[b+2:]
        try:
            
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('i', i)
            bytesJPEG = bytes() 
            if cv2.waitKey(1) == 27:
                exit(0)
        except Exception as e:
            pass
        
        
#%%

import cv2
import urllib.request
import numpy as np
import threading
import matplotlib.pyplot as plt
import time
import PIL
import io

isRunning = True

def performThread(url):
    nFrames = 0
    nErrors = 0
    baseUrl=url+":81/stream.mjpeg"
    stream = urllib.request.urlopen(baseUrl)
    bytesJPEG = bytes()
    t1 = time.time()
    while isRunning:
        bytesJPEG += stream.read(1024)
        a = bytesJPEG.find(b'\xff\xd8')
        b = bytesJPEG.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytesJPEG[a:b+2]
            bytesJPEG = bytesJPEG[b+2:]
            
            try:
                if(1):
                    # Convert bytes to stream (file-like object in memory)
                    picture_stream = io.BytesIO(jpg)
                    
                    # Create Image object
                    picture = PIL.Image.open(picture_stream)
                else:
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    picture = np.mean(frame,-1)
                    
                nFrames+=1
                #print(url+" - nFrames"+str(nFrames))
                
                #plt.title(baseUrl)
                #plt.imshow(picture), plt.show()
                print(url+" - Framerate: "+str(1/(time.time()-t1)))
                t1 = time.time()
                stream.flush()
                #cv2.imshow(url, picture)
                bytesJPEG = bytes() 
                #if cv2.waitKey(1) & 0xFF ==ord('e'):
                #    break
            except Exception as e:
                #print(e) 
                nErrors+=1
                #print(url+" - nErrors"+str(nErrors))
                pass
        
        time.sleep(.1)


url1 = "http://192.168.2.166"
url2 = "http://192.168.2.164"
            
thread1 = threading.Thread(target=performThread, args=(url1,))
thread1.start()
   
thread2 = threading.Thread(target=performThread, args=(url2,))
thread2.start()
'''
thread3 = threading.Thread(target=performThread)
thread3.start()
'''
#%%

# import required libraries
from vidgear.gears import CamGear
import cv2


# open any valid video stream(for e.g `myvideo.avi` file)
sourceFile = "http://192.168.2.174:81/stream.mjpeg"
stream = CamGear(source=sourceFile).start()

# loop over
while True:

    # read frames from stream
    frame = stream.read()

    # check for frame if Nonetype
    if frame is None:
        break

    # {do something with the frame here}

    # Show output window
    cv2.imshow("Output", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close video stream
stream.stop()
    
            
#%%

import cv2
import urllib.request
import numpy as np
import threading
import time



def threadFunc(url):
    stream = urllib.request.urlopen(url)
    t1=time.time()
    bytesJPEG = bytes()

    while True:
        print("start capturing")
        bytesJPEG += stream.read(1024)
        a = bytesJPEG.find(b'\xff\xd8')
        b = bytesJPEG.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytesJPEG[a:b+2]
            bytesJPEG = bytesJPEG[b+2:]
            try:
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                print(url+" - Framerate: "+str(1/(time.time()-t1)))
                t1 = time.time()
                cv2.imshow(url, i)
            except:
                pass
         
url1 = "http://192.168.2.166:81/stream.mjpeg"
url2 = "http://192.168.2.164:81/stream.mjpeg"
            
#threadFunc()
cv2.namedWindow(url1, cv2.WINDOW_NORMAL)
thread1 = threading.Thread(target=threadFunc, args=(url1,))
thread1.setDaemon(True)
thread1.start()

if cv2.waitKey(1) == 27:
    exit(0)


asdf
cv2.namedWindow(url2, cv2.WINDOW_NORMAL)
thread2 = threading.Thread(target=threadFunc, args=(url2,))
thread2.start()
   

#%%
# encoding: utf-8
import threading
import time
import cv2
import numpy as np

def multiThreadSub():
    img = np.uint8(1005*np.random.rand(100,100))
    #img = cv2.imread('input.png')
    # サブスレッドからimshowは可能
    cv2.imshow('window', img)

def multiThread():
    # メインスレッドで
    cv2.namedWindow('window')
    # スレッドを立てる
    t = threading.Thread(target=multiThreadSub, name='sub')
    t.setDaemon(True)
    t.start()
    # メインスレッド内でwaitKey
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def singleThread():
    img = np.uint8(1005*np.random.rand(100,100))
    #img = cv2.imread('input.png')
    cv2.imshow('window', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__=='__main__':
    #singleThread()
    multiThread()