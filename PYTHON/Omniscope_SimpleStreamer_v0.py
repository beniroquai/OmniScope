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
base_url = "http://192.168.2."
port  = "80"
individual_url = ("152", "153") #, "24")
file_endpoint = "/cam-hi.jpg"
video_endpoint = "/cam.mjpeg"


# determine all URLS
urls = []
for i_url in individual_url:
    urls.append(base_url+i_url+":"+port+file_endpoint)



video_url = base_url+individual_url[0]+":"+port+video_endpoint

import cv2
import urllib.request
import numpy as np

stream = urllib.request.urlopen('http://localhost:8000/camera/mjpeg?type=.mjpg')
bytes = b''
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8') #frame starting 
    b = bytes.find(b'\xff\xd9') #frame ending
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imshow('image', img)
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            break
# Open a URL stream
stream = cv2.VideoCapture(video_url)
while ( stream.isOpened() ):
    # Read a frame from the stream
    ret, img = stream.read()
    if ret: # ret == True if stream.read() was successful
        cv2.imshow('Video Stream Monitor', img)





while True:
    time1 = time.time()
    image_list = []
    for i_cam_url in urls:
    
        imgResp=urllib.request.urlopen(i_cam_url)
        imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
        img=cv2.imdecode(imgNp,-1)
        img = np.mean(img, -1)
        image_list.append(img)
    
    # tile images
    large_image = 0
    for i_image in image_list:
        if type(large_image) is not np.ndarray and large_image == 0:
            large_image = np.expand_dims(i_image, -1)
        else:
            large_image = np.hstack((large_image, np.expand_dims(i_image, -1)))
        
    print("It took me: "+str(time.time()-time1)+" s")
    # display image
    plt.imshow(large_image, cmap = 'gray')
    plt.title("Omsnicope Wells")
    plt.show()
            
        
    
        
    