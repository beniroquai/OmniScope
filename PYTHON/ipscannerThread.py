import requests
import numpy as np
import threading
import time

allScopes = []

# Define a function for the thread
def findOmniscope(subnet="", ipRange=(0,50),endpoint="/getID"):
    endpoint="/getid"
    print("searching in range: "+str(ipRange))
    for ip in range(*ipRange):
       URL = subnet+str(ip)+endpoint
       #print(URL)
       try:
           source = requests.get(URL,timeout=0.5)
           if(str(source.content).find("OMNISCOPE")>0):
               allScopes.append(subnet+str(ip))
       except :
           pass
       
def findOmniscopes(subnet, nThreads = 20):
    findScopeThreads = []
    for iThread in range(np.int32(np.ceil(255/nThreads))):
        findScopeThreads.append(threading.Thread(target=findOmniscope, args=(subnet, (nThreads*iThread,iThread*nThreads+nThreads), "/getID")))
        findScopeThreads[-1].start()
        
    print("Waiting to finish the search in "+str(nThreads)+" Threads")
    while(True):
        isAlive = True
    
        for iThread in findScopeThreads:
            isAlive &= iThread.is_alive()
        if not isAlive:
            break
    
    

    return allScopes
        
        
allOmniscopes = findOmniscopes("http://192.168.2.",nThreads=40)

print(allOmniscopes)