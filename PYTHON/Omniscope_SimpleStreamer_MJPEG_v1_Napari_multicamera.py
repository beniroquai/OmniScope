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

individual_url = ["43", "247"]
urls=[]
for i_url in individual_url:
    urls.append(base_url+i_url)

#%% controls
class MultiCameraClient(object):
    def __init__(self, urls, port=80, is_debug=False):
        self.urls = urls 
        self.port = port
        self.is_debug = is_debug
        self.microscope_list = []
        self.is_streaming = False
        
        # image dimensions 
        self.pix_x = 600
        self.pix_y = 800
        self.Nx = 4 
        self.Ny = 6
        self.image_list = None
        
        for urli in urls:
            print("Connecting to microscope: "+urli)
            self.microscope_list.append(utils.ESP32Client(urli, self.port, is_debug=self.is_debug))
            
    def list_microscopes(self):
        for microscope_i in self.microscope_list:
            print(microscope_i.get_id())
            
    def start_streams(self, callback_fct=None):
        if not self.is_streaming:
            self.is_streaming = True        
            for microscope_i in self.microscope_list:
                microscope_i.start_stream(callback_fct)
            
            # wait until all cameras start frame acquisition
            print("Let the cameras warm up")
            is_ready = True
            while(not is_ready):
                is_ready = True
                for microscope_i in self.microscope_list:
                    is_ready = is_ready and microscope_i.last_frame
                time.sleep(.5)

    def stop_streams(self):
        self.is_streaming = False        
        for microscope_i in self.microscope_list:
            microscope_i.stop_stream()
            
    def acquire(self):
        # sample images as they become available
        self.image_canvas = np.zeros((self.Nx*self.pix_x, self.Ny*self.pix_y))
        try:
            self.image_list = []
            if self.is_streaming:
                for microscope_i in self.microscope_list:
                    self.image_list.append(microscope_i.last_frame)
                    
            # merge images
            if self.image_list is not None:
                iiter = 0
                for microscope_i in self.microscope_list:
                    pos_x = microscope_i.setup_id//self.Nx
                    pos_y =  microscope_i.setup_id%self.Nx
                    iimage = self.image_list[iiter]
                    self.image_canvas[pos_x*self.pix_x:(1+pos_x)*self.pix_x,
                                      pos_y*self.pix_y:(1+pos_y)*self.pix_y] = iimage
                    
                    iiter +=1

        except:
            print("Need to wait until frames become available...")
        
        return self.image_list, self.image_canvas


OmniscopeClient = MultiCameraClient(urls, is_debug=False)
OmniscopeClient.list_microscopes()
OmniscopeClient.start_streams()

while(True):
    t1=time.time()
    allframes, mergedimage = OmniscopeClient.acquire()
    print(1/(time.time()-t1))
    cv2.imshow('merged image',np.uint8(np.stack((mergedimage, mergedimage, mergedimage), -1)))
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
   

OmniscopeClient.stop_streams()

#%%
asdf

host = "192.168.43.43"
host = "192.168.43.247"
esp32 = utils.ESP32Client(host, 80, is_debug=True)

if(0):

    esp32.set_flash(1)
    esp32.set_led(1)
    esp32.set_id(11)
    setup_id = esp32.get_id()
    print(setup_id)
    #esp32.restart()

#%% stream
viewer = napari.Viewer()

def display_image(image, is_napari=False):
    if is_napari:
        viewer.add_image(image)

    else:
        plt.imshow(image, cmap='gray')
        plt.show()

    
esp32.start_stream(callback_fct=display_image)
time.sleep(5)
esp32.stop_stream()


plt.imshow(esp32.getframe())

# %% single capture
esp32.soft_trigger()
myframe = esp32.getframe()

plt.imshow(myframe)
plt.show()

myframe = esp32.getframe(is_triggered=True)
        
plt.imshow(myframe)
plt.show()      
    