# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 07:14:48 2021

@author: diederichbenedict
"""
import urllib
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import urllib

# define all cameras


class CameraUnit:
    def __init__(self, url, cam_id):
        self.base_url = "http://192.168.2."
        self.port  = "80"
        self.url = url
        self.cam_id = cam_id
        self.file_endpoint = "/cam-hi.jpg"
        self.video_endpoint = "/cam.mjpeg"
        
        self.CAMERA_BUFFRER_SIZE=4096
       
    
    def start_stream(self):
        #% MJPEG
        video_url = self.base_url+self.url+":"+self.port+self.video_endpoint
        stream = urllib.request.urlopen(video_url)
        bts=b''
        while True:
            bts+=stream.read(CAMERA_BUFFRER_SIZE)
            jpghead=bts.find(b'\xff\xd8')
            jpgend=bts.find(b'\xff\xd9')
            try:
                if jpghead>-1 and jpgend>-1:
                    jpg=bts[jpghead:jpgend+2]
                    bts=bts[jpgend+2:]
                    img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR) 
                    cv2.imshow('Window name',img) # display image while receiving data
                    if cv2.waitKey(1) ==27: # if user hit esc
                        exit(0) # exit program        
            except:
                print("Wrong image..")
        


individual_url = ("152", "153") #, "24")

# determine all URLS
urls = []
for i_url in individual_url:
    urls.append(base_url+i_url+":"+port+file_endpoint)

#%% 
#%load_ext autoreload
#%autoreload 2

from utils import *
host = "192.168.43.5"
esp32 = ESP32Client(host, 80)

esp32.set_led(1)
esp32.set_id(0)
setup_ids = esp32.get_id()
esp32.restart()

#%% JPEG 
while(True):
    imgResp=urllib.request.urlopen(urls[1])
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    img=cv2.imdecode(imgNp,-1)

    # all the opencv processing is done here
    cv2.imshow('test',img)
    if ord('q')==cv2.waitKey(10):
        exit(0)  
        
        