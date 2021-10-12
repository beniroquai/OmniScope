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
import utils
import napari
%gui qt5

#%load_ext autoreload
#%autoreload 2

#%% determine all camera URLS
individual_url = ("247") #, "24")
base_url = "192.168.43."
port = "80"

urls = []
for i_url in individual_url:
    urls.append(base_url+i_url+":"+port)

#%% controls
host = "192.168.43.247"
esp32 = utils.ESP32Client(host, 80, is_debug=True)

if(0):

    esp32.set_flash(1)
    esp32.set_led(1)
    esp32.set_id(10)
    setup_id = esp32.get_id()
    print(setup_id)
    #esp32.restart()

#%% stream
viewer = napari.Viewer()

def display_image(image, is_napari=True):
    if is_napari:
        viewer.add_image(image)

    else:
        plt.imshow(image, cmap='gray')
        plt.show()

    
esp32.start_stream(callback_fct=display_image)
time.sleep(5)
esp32.stop_stream()


plt.imshow(esp32.last_frame)

# %% single capture
esp32.soft_trigger()
myframe = esp32.getframe()

plt.imshow(myframe)
plt.show()

myframe = esp32.getframe(is_triggered=True)
        
plt.imshow(myframe)
plt.show()      
    