import requests
import json
import time
import io
import logging
import zeroconf
import scapy.all as scapy
import urllib
import numpy as np
import cv2
import imageio

from threading import Thread



class ESP32Client(object):
    # headers = {'ESP32-version': '*'}
    headers={"Content-Type":"application/json"}

    def __init__(self, host, port=80, is_debug=False):
        if isinstance(host, zeroconf.ServiceInfo):
            # If we have an mDNS ServiceInfo object, try each address
            # in turn, to see if it works (sometimes you get addresses
            # that don't work, if your network config is odd).
            # TODO: figure out why we can get mDNS packets even when
            # the microscope is unreachable by that IP
            for addr in host.parsed_addresses():
                if ":" in addr:
                    self.host = f"[{addr}]"
                else:
                    self.host = addr
                self.port = host.port
                try:
                    self.get_json(self.base_uri)
                    break
                except:
                    logging.info(f"Couldn't connect to {addr}, we'll try another address if possible.")
        else:
            self.host = host
            self.port = port
            #self.get_json(self.base_uri)
        #self.populate_extensions()
        self.is_stream = False
        self.latest_frame = None
        self.is_debug = is_debug
        self.setup_id = -1

        
    @property
    def base_uri(self):
        return f"http://{self.host}:{self.port}"

    def get_json(self, path):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}, headers=None, timeout=10):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        if headers is None:
            headers = self.headers
            
        r = requests.post(path, json=payload, headers=headers,timeout=timeout)
        r.raise_for_status()
        r = r.json()
        return r


    def get_temperature(self):
        path = "/temperature"
        r = self.get_json(path)
        return r['value']
    
    #% LED
    def set_led(self, state=0):
        payload = {
            "value": state
        }
        path = '/led'
        if state:
            print("WARNING: TRIGGER won't work if LED is turned on!")
        r = self.post_json(path, payload)
        return r
    
    def set_flash(self, state=0):
        payload = {
            "value": state
        }
        path = '/flash'
        r = self.post_json(path, payload)
        return r
    
    def set_id(self, m_id=0):
        payload = {
            "value": m_id
        }
        path = '/setID'
        r = self.post_json(path, payload)
        self.setup_id = r
        return r
    
    def get_id(self):
        path = '/getID'
        r = self.get_json(path)
        self.setup_id = r
        return r
    
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
        self.stream_url = self.base_uri+'/cam-stream'
        self.is_stream = True
        self.frame_receiver_thread = Thread(target = self.getframes)
        self.frame_receiver_thread.start() 
        self.callback_fct = callback_fct

    def stop_stream(self):
        # Create and launch a thread    
        self.is_stream = False
        self.frame_receiver_thread.join()

    def getframe(self, is_triggered=False):
        url = self.base_uri+"/cam.jpg"
        if is_triggered:
            url = self.base_uri+"/cam-triggered"
        return np.mean(np.array(imageio.imread(url)), -1)
        
    def getframes(self):
        if self.is_debug:  print("Start Stream - "+str(self.setup_id))
        self.last_frame = None
        while self.is_stream:
            t1 = time.time()
            url = self.base_uri+"/cam.jpg"
            try:
                frame = imageio.imread(url)
                self.last_frame = np.mean(frame, -1)
            except:
                frame = np.zeros((100,100))
                print("Error while reading frame")
            if self.callback_fct is not None:
                self.callback_fct(self.last_frame)
            if self.is_debug: print("Framerate: "+str(1/(time.time()-t1)))
        if self.is_debug: print("Stop Stream")
        
    def soft_trigger(self):
        path = '/softtrigger'
        r = self.post_json(path)
        return r
            
            
def scan(ip):
    arp_req_frame = scapy.ARP(pdst = ip)

    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 1, verbose = False)[0]
    result = []
    for i in range(0,len(answered_list)):
        #client_dict = {"ip" : answered_list[i][1].psrc, "mac" : answered_list[i][1].hwsrc}
        #result.append(client_dict)
        result.append(answered_list[i][1].psrc)

    return result,answered_list

        

    
