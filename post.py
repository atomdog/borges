import numpy as np
import tables
import matplotlib.pyplot as plt
import os
from datetime import datetime
import shutil
import json
import pandas as pd
import threading
import pickle
import zmq
import random 
import threading

def generate_request_id():
    a = random.random()
    b = random.random()
    c = random.random()
    idv = hash(a*b*c)
    idv = hash(hash)
    return(idv)

class channel(threading.Thread):
    def __init__(self, name, iq, oq):
        print("launching line on channel: " + name)
        self.stop_issued = threading.Event()
        threading.Thread.__init__(self)
        self.name = name
        self._iqueue = iq
        self._oqueue = oq
        self.ctx = zmq.Context()
        
    #thread methods
    #thread runtime
    def run(self):
        try:
            
            o_socket = self.ctx.socket(zmq.PUSH)
            o_socket.bind('ipc:///tmp/'+self.name+'.pipe')
            print("output bound on channel: ", self.name)
            i_socket = self.ctx.socket(zmq.PULL)
            i_socket.bind('ipc:///tmp/'+self.name+'.pipe')
            print("input bound on channel: ", self.name)
            breaker=False
            #enter into thread runtime
            
            while(not breaker):
                    
                #without blocking, check if there is a message being received by the socket
                try:
                    message = i_socket.recv(flags=zmq.NOBLOCK)
                    print(message)
                except Exception as e:
                    print(e)
                    message = None
                if(message!=None):
                    print(message)
                    self._iqueue.put(message)
                    pass
                
                if(not self._oqueue.empty()):
                    
                    ob = self._oqueue.get()
                    print(ob)
                    msg = pickle.dumps(ob)
                    print(msg)
                    o_socket.send(msg)

            if self.stopped():
                return
            else:
                self.stop()
                breaker=True
            return
        except Exception as e:
            print(e)
            self.stop()
            return(-1)

    def stop(self):
        #set stop event
        print("worker ", self.filename, " stopping")
        self.closeFile()
        self.stop_issued.set()
    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()
