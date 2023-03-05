import requests
import json
import time
import io
import logging
import numpy as np
import urllib.request
import requests
import numpy as np
import threading
import time

from threading import Thread

from esp32camera import ESP32Camera


    

# TODO: Make MultiCameraClient a child of the single camera module
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
        self.port = 80
        self.image_list = None
        
        for urli in urls:
            print("Connecting to microscope: "+urli)
            camera = ESP32Camera(urli, port=self.port, is_debug=False)
            self.microscope_list.append(camera)
            
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
            '''
            while(not is_ready):
                is_ready = True
                for microscope_i in self.microscope_list:
                    is_ready = is_ready and microscope_i.last_frame
                time.sleep(.5)
            '''
                
    def setGain(self, gain=0, cameraIndex=-1):
        if cameraIndex == -1:
            for microscope_i in self.microscope_list:
                microscope_i.setGain(gain)
        else:
            self.microscope_list[cameraIndex].setGain(gain)
            
    def setExposureTime(self, exposureTime=10, cameraIndex=-1):
        if cameraIndex == -1:
            for microscope_i in self.microscope_list:
                microscope_i.setExposureTime(exposureTime)
        else:
            self.microscope_list[cameraIndex].setExposureTime(exposureTime)

    def setFrameSize(self, frameSize=3, cameraIndex=-1):
        if cameraIndex == -1:
            for microscope_i in self.microscope_list:
                microscope_i.setFrameSize(framesize=frameSize)
        else:
            self.microscope_list[cameraIndex].setFrameSize(framesize=frameSize)
                        
    def setLed(self, ledIntensity=3, cameraIndex=-1):
        if cameraIndex == -1:
            for microscope_i in self.microscope_list:
                microscope_i.setLed(ledIntensity=ledIntensity)
        else:
            self.microscope_list[cameraIndex].setLed(ledIntensity=ledIntensity)

    def stop_streams(self):
        self.is_streaming = False        
        for microscope_i in self.microscope_list:
            microscope_i.stop_stream()
            
    def acquire(self):
        # sample images as they become available
        self.image_canvas = np.zeros((self.Nx*self.pix_x, self.Ny*self.pix_y))
        self.image_list = []
        if self.is_streaming:
            for microscope_i in self.microscope_list:
                self.image_list.append(microscope_i.frame)
                
        # merge images
        '''
        if self.image_list is not None:
            iiter = 0
            for microscope_i in self.microscope_list:
                pos_x = microscope_i.setup_id//self.Nx
                pos_y =  microscope_i.setup_id%self.Nx
                iimage = self.image_list[iiter]
                self.image_canvas[pos_x*self.pix_x:(1+pos_x)*self.pix_x,
                                  pos_y*self.pix_y:(1+pos_y)*self.pix_y] = iimage
                
                iiter +=1
        '''
        iIter = 0
        for iImage in self.image_list:
            if iIter == 0:
                self.image_canvas = iImage
            else:
                self.image_canvas = np.hstack((self.image_canvas,iImage))
            iIter += 1
            


        return self.image_list, self.image_canvas


class IPScanner(object):
    
    def __init__(self):
        self.allScopes = []

    # Define a function for the thread
    def findOmniscope(self, subnet="", ipRange=(0,50),endpoint="/getID"):
        endpoint="/getid"
        print("searching in range: "+str(ipRange))
        for ip in range(*ipRange):
            URL = subnet+str(ip)+endpoint
            #print(URL)
            try:
                source = requests.get(URL,timeout=0.5)
                if(str(source.content).find("OMNISCOPE")>0):
                    self.allScopes.append(subnet+str(ip))
            except :
                pass
        
    def findOmniscopes(self, subnet, nThreads = 20):
        findScopeThreads = []
        stepRange = np.int32(np.ceil(255/nThreads))
        for iThread in range(nThreads):
            findScopeThreads.append(threading.Thread(target=self.findOmniscope, args=(subnet, (stepRange*iThread,iThread*stepRange+stepRange), "/getID")))
            findScopeThreads[-1].start()
            
        print("Waiting to finish the search in "+str(nThreads)+" Threads")
        while(True):
            isAlive = True
            for iThread in findScopeThreads:
                isAlive &= iThread.is_alive()
            if not isAlive:
                break
        print("Done. Found: "+ str(len(self.allScopes))+" scopes")
        return self.allScopes
            
            
    
