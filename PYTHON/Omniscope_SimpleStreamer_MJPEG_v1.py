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


individual_url = ("152", "153") #, "24")

# determine all URLS
urls = []
for i_url in individual_url:
    urls.append(base_url+i_url+":"+port+file_endpoint)

#%% controls
#%load_ext autoreload
#%autoreload 2

import utils
host = "192.168.43.247"
esp32 = utils.ESP32Client(host, 80)

esp32.set_flash(1)
esp32.set_led(1)
esp32.set_id(10)
setup_id = esp32.get_id()
print(setup_id)
#esp32.restart()


#%% stream
import utils
import time
host = "192.168.43.247"
esp32 = utils.ESP32Client(host, 80, is_debug=True)

esp32.start_stream()
time.sleep(2)
esp32.stop_stream()

import matplotlib.pyplot as plt
plt.imshow(esp32.latest_frame)

# %% single capture
esp32.soft_trigger()
myframe = esp32.getframe()

plt.imshow(myframe)
plt.show()

myframe = esp32.getframe(is_triggered=True)
        
plt.imshow(myframe)
plt.show()      
    