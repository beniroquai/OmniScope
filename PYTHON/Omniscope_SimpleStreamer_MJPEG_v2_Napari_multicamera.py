# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 07:14:48 2021

@author: diederichbenedict
"""
#%%
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

OmniscopeClient = utils.MultiCameraClient(urls, is_debug=False)
OmniscopeClient.list_microscopes()
OmniscopeClient.start_streams()


from napari.qt.threading import thread_worker


@thread_worker
def grab_frame():
    allframes, mergedimage = OmniscopeClient.acquire()
    return mergedimage

viewer = napari.Viewer()
worker = grab_frame()  # create "worker" object
worker.returned.connect(viewer.add_image)  # connect callback functions
worker.start()  # start the thread!
napari.run()


OmniscopeClient.stop_streams()


#%%

from napari._qt.qthreading import thread_worker
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpinBox, QCheckBox, QGridLayout, QLabel
from magicgui import magic_factory
import cv2
from ._function import acquire

class ContinuousAcquisition(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.image_layer = None
        self.camera_device = None
        self.worker = None
        self.acquisition_count = 0


        self.acquisition_count += 1
        self.camera_device = cv2.VideoCapture(self.camera_index_spinner.value())

        # Multi-threaded interaction
        # inspired by https://napari.org/docs/dev/events/threading.html
        def update_layer(data):
            for name, image in data.items():
                if image is not None:
                    try:
                        # replace layer if it exists already
                        self.viewer.layers[name].data = image
                    except KeyError:
                        # add layer if not
                        self.viewer.add_image(
                            image, name=name, blending='additive'
                        )

        @thread_worker
        def yield_acquire_images_forever():
            while self.viewer.window.qt_viewer:  # loop until napari closes
                if self.camera_device:
                    yield {'image' + str(self.acquisition_count): acquire(keep_connection=True, device=self.camera_device, rgb=self.rgb_checkbox.isChecked())}
                time.sleep(0.05)

        # Start the imaging loop
        if self.worker is None:
            self.worker = yield_acquire_images_forever()
            self.worker.yielded.connect(update_layer)
            self.worker.start()


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
    