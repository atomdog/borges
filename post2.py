import asyncio
import zmq.asyncio
import pickle 
import zmq
import json
import time
import threading
import queue

class channel(threading.Thread):
    def __init__(self, name, channel_type, iq, oq):
        self.name = name
        threading.Thread.__init__(self)
        self._iqueue = iq
        self._oqueue = oq
        if(channel_type == "server"):
            self.incoming_label = 'requests'
            self.outgoing_label = 'responses'
        elif(channel_type == "client"):
            self.incoming_label = 'responses'
            self.outgoing_label = 'requests'
        self.ctx = zmq.Context()
        self.stop_issued = threading.Event()
        print("- post -> configured channel: "+ self.name)
        pass

    def receive(self):
        print("- post -> opening inbound channel", self.name)
        ctx = self.ctx
        socket = ctx.socket(zmq.PULL)
        socket.bind('ipc:///tmp/'+self.name+'_'+self.incoming_label+'.pipe')
        print("- post -> opened inbound channel", self.name)
        while(stop_issued.is_set() is False):
            try:
                #check for a message, this will not block
                message = socket.recv(flags=zmq.NOBLOCK)
            except zmq.Again as e:
                message = None
            yield message

    def send(self):
        print("- post -> opening outbound channel", self.name)
        ctx = self.ctx
        socket = ctx.socket(zmq.PUSH)
        socket.bind('ipc:///tmp/'+self.name+'_'+self.outgoing_label+'.pipe')
        print("- post -> opened outbound channel", self.name)
        while(stop_issued.is_set() is False):
            try:
                if(self._oqueue.empty() == False):
                    msg = self._oqueue.get()
                    print("- post -> outbound on "+self.name+" -> ")
                    msg = pickle.dumps(msg) 
                    print(msg)
                    socket.send(msg)
            except:
                pass
            yield True
    def run(self):
        i = self.receive()
        i = self.send()
        try:
            print("- post -> launched channel: "+ self.name)
            breaker=False
            while(not breaker):
                #do while breaker is not tripped by one of the kill conditions

                #if the 'to be sent' queue is empty
                if(not self._oqueue.empty()):
                    pass
                #if the 'received' is empty
                if(not self._iqueue.empty()):
                    pass
                
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
        print("worker ", self.name, " stopping")
        self.stop_issued.set()
    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()