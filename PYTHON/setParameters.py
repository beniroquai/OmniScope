#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 21:37:05 2022

@author: bene
"""
import requests

payload={"brightness": 2,
         "quality": 1,
         "effect": 25}
headers={"Content-Type":"application/json"}
x = requests.post('http://192.168.2.171/postjson', json=payload, headers=headers)
print(x.status_code)

