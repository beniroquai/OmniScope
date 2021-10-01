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
# define all cameras
base_url = "http://192.168.43."
port  = "80"
individual_url = ("134", "74", "24")
file_endpoint = "/cam-hi.jpg"
urls = []
for i_url in individual_url:
    urls.append(base_url+i_url+":"+port+file_endpoint)

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
            
        
    
        
    