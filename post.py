import numpy as np
import tables
import matplotlib.pyplot as plt
import os
from datetime import datetime
import shutil
import json
import pandas as pd

import pickle
import asyncio
import zmq
import zmq.asyncio
import random 

def generate_request_id():
    a = random.random()
    b = random.random()
    c = random.random()
    idv = hash(a*b*c)
    idv = hash(hash)
    return(idv)
# a line opens a connection when a message needs to be sent and waits for the response before exiting
# opens line, sends request, waits for response, closes
class line:
    def __init__(self, name):
        self.incoming_request_queue = asyncio.Queue()
        self.outgoing_request_queue = asyncio.Queue()
        self.ctx = zmq.asyncio.Context()
        self.request_id = generate_request_id()
        
        self.name = name

    #handles incoming requests
    #waits for incoming requests and adds them to incoming request queue
    #waits for a response. this is a one way pipe.

    async def incoming(self):
        ctx = self.ctx
        socket = ctx.socket(zmq.PULL)
        socket.connect('ipc:///tmp/'+self.name+'_inbound.pipe')
        #print("Listening...")
        this_response = False
        while(not this_response):
            msg = await socket.recv() # waits for msg to be ready
            if(pickle.loads(msg)['REQ_ID'] == self.request_id):
                await self.incoming_request_queue.put(msg)
                this_response=True


    #handles outgoing responses
    #waits for outgoing request queue update and sends them to socket
    async def outgoing(self):
        ctx = self.ctx
        #print("Outgoing connecting...")
        socket = ctx.socket(zmq.PUSH)
        socket.connect('ipc:///tmp/'+self.name+'_outbound.pipe')
        #socket.send(msg)
        call = self.call
        
        msg = pickle.dumps(call)
        #print("Sending... ", call)
        await socket.send(msg)
        
    async def main(self):
        #sends, and then waits for the response
        await asyncio.gather(self.outgoing(),self.incoming())
        self.return_value = await self.incoming_request_queue.get()

    def run(self, call):
        self.call = call
        asyncio.run(self.main())
        return(pickle.loads(self.return_value))
        
    def close(self, call):
        self.call = call
        asyncio.run(self.main())
        return(pickle.loads(self.return_value))


