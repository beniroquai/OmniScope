import requests
import numpy as np
import threading
import time
import json

allScopes = []

# Define a function for the thread
def findOmniscope(subnet="", ipRange=(0,50),endpoint="/status"):
    print("searching in range: "+str(ipRange))
    for ip in range(*ipRange):
       URL = subnet+str(ip)+endpoint
       #print(URL)
       try:
            source = requests.get(URL,timeout=0.5)
            omniscopeID = source.json()['omniscope']
            omniscopeIP = source.json()['stream_url'].split(":8")[0]
            allScopes.append({"IP":omniscopeIP,
                              "ID":omniscopeID})
       except :
           pass
       
def findOmniscopes(subnet, nThreads = 20):
    findScopeThreads = []
    for iThread in range(np.int32(np.ceil(255/nThreads))):
        findScopeThreads.append(threading.Thread(target=findOmniscope, args=(subnet, (nThreads*iThread,iThread*nThreads+nThreads), "/status")))
        findScopeThreads[-1].start()
    print("Waiting to finish the search in "+str(nThreads)+" Threads")
    while(True):
        isAlive = True
        for iThread in findScopeThreads:
            isAlive &= iThread.is_alive()
        if not isAlive:
            break
    
    

    return allScopes
        

baseURL = "http://192.168.43."
        
allOmniscopes = findOmniscopes(baseURL, nThreads=40)

print(allOmniscopes)



# %%
