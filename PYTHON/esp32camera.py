#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 17:11:38 2022

@author: bene
"""

from PIL import Image
import io
import requests
import time
import cv2
import numpy as np
from threading import Thread
import urllib


class logger(object):
    def __init__(self):
        pass
    
    def error(self, message):
        print(message)

    def debug(self, message):
        print(message)
        
class ESP32Camera(object):
    # headers = {'ESP32-version': '*'}
    headers={"Content-Type":"application/json"}

    def __init__(self, host, port=80, is_debug=False):
        self.host = host
        self.port = port
        #self.get_json(self.base_uri)
        #self.populate_extensions()
        self.is_stream = False

        self.is_debug = is_debug
        self.setup_id = -1
        
        self.SensorWidth = 640
        self.SensorHeight = 460
        self.exposuretime = 0
        self.gain = 0
        self.framesize = 0
        
        self.__logger = logger()
        
        self.frame = -np.ones((self.SensorHeight,self.SensorWidth))

        
    @property
    def base_uri(self):
        return f"{self.host}:{self.port}"

    def get_json(self, path, isJson=True):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path)
        r.raise_for_status()
        if isJson:
            return r.json()
        else:
            return r


    def post_json(self, path, payload={}, headers=None, isJson = True, timeout=10):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        if headers is None:
            headers = self.headers
            
        r = requests.post(path, json=payload, headers=headers,timeout=timeout)
        r.raise_for_status()
        if isJson:
            r = r.json()
        return r


    #% LED
    def setLed(self, ledIntensity=0):
        payload = {
            "ledintensity": ledIntensity
        }
        path = '/postjson'
        r = self.post_json(path, payload, isJson = False)
        return r
    
    def set_id(self, m_id=0):
        payload = {
            "value": m_id
        }
        path = '/setID'
        r = self.post_json(path, payload, isJson = False)
        self.setup_id = r
        return r
    
    def setGain(self, gain=0):
        payload = {
            "gain": gain
        }
        path = '/postjson'
        r = self.post_json(path, payload, isJson = False)
        return r
    
    def setExposureTime(self, exposureTime=0):
        payload = {
            "exposuretime": exposureTime
        }
        path = '/postjson'
        r = self.post_json(path, payload, isJson = False)
        return r
    
    def setFrameSize(self, framesize=0):
        payload = {
            "framesize": framesize
        }
        path = '/postjson'
        r = self.post_json(path, payload, isJson = False)
        return r
   
    
    def get_id(self):
        path = '/getid'
        r = self.get_json(path, isJson=False)
        self.setup_id = str(r.content).split("b'")[-1]
        return self.setup_id
    
    def is_omniscope(self):
        path = '/identifier'
        r = self.post_json(path)
        return r.find("OMNISCOPE")>=0

    def restart(self):
        path = '/restart'
        r = self.post_json(path)
        return r

    def start_stream(self, callback_fct = None):
        # Create and launch a thread    
        self.stream_url = self.host+":81/stream.mjpeg"
        
        self.is_stream = True
        self.frame_receiver_thread = Thread(target = self.getframes, args=(self.stream_url,), daemon=True)
        self.frame_receiver_thread.start() 
        self.callback_fct = callback_fct

    def stop_stream(self):
        # Create and launch a thread    
        self.is_stream = False
        self.frame_receiver_thread.join()

    def getframe(self, is_triggered=False):
        url = self.host+":80/capture"
        response = requests.get(url)
        bytes_im = io.BytesIO(response.content)
        frame = np.uint8(np.mean(np.array(Image.open(bytes_im)), -1))
        return frame
        
    def getframes(self, url):           
        bytesJPEG = bytes()
        try:
            stream = urllib.request.urlopen(url, timeout=5)
        except Exception as e:
            self.is_stream = False
            self.__logger.error("Stream could not be opened")
            self.__logger.error(e)
        frameId = 0
        errorCounter = 0
        while self.is_stream:
            try:
                bytesJPEG += stream.read(2**14)
                a = bytesJPEG.find(b'\xff\xd8')
                b = bytesJPEG.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytesJPEG[a:b+2]
                    bytesJPEG = bytesJPEG[b+2:]
                    try:
                        frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        frame = np.mean(frame,-1)
                        # flush stream and reset bytearray
                        stream.flush()
                        bytesJPEG = bytes() 
                        if self.is_debug:  
                            self.__logger.debug("Frame#"+str(frameId))
                            self.__logger.debug("Error#"+str(errorCounter))
                        frameId += 1
                        
                        if self.callback_fct is not None:
                            self.callback_fct(frame)
                        else:
                            self.frame = frame
                        
                    except Exception as e:
                        errorCounter+=1
                    
                    # limit thread workload
                    time.sleep(.1)

                    
            except Exception as e:
                # reopen stream?
                self.__logger.error(e)
                stream = urllib.request.urlopen(url, timeout=2)


        
    def soft_trigger(self):
        path = '/softtrigger'
        r = self.post_json(path)
        return r
    
    


        
# Copyright (C) ImSwitch developers 2021
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.