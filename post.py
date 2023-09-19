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
        threading.Thread.__init__(self)
        self.name = name
        
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

        self.poller = zmq.Poller()
        print("- post -> configured channel: "+ self.name)
        pass

                #print(message)
            
            

    def out(self):
        print("- post -> opening outbound channel", self.name)
        sender = self.ctx.socket(zmq.PUSH)
        
        sender.connect('ipc:///tmp/'+self.name+'_'+self.outgoing_label+'.pipe')
        print("- post -> opened outbound channel", self.name)
        while(self.stop_issued.is_set() is False):
            try: 
                if(self._oqueue.empty() == False):
                    msg = self._oqueue.get()
                    print("- post -> outbound on "+self.name+" -> ")
                    msg = pickle.dumps(msg)
                    try:
                        sender.send(msg)
                    except Exception as e:
                        print(e)
                    #print(msg)
            except:
                pass

            yield True

        sender.close()

    def run(self):
        try:
            print("- post -> opening inbound channel", self.name)
            socket = self.ctx.socket(zmq.PULL)
            socket.bind('ipc:///tmp/'+self.name+'_'+self.incoming_label+'.pipe')
            self.poller.register(socket, zmq.POLLIN)
            print("- post -> opened inbound channel", self.name)
            print("- post -> launched channel: "+ self.name)

            o = self.out()
            next(o)

            while(self.stop_issued.is_set() is False):
                try:
                    socks = dict(self.poller.poll(0))
                    if socket in socks and socks[socket] == zmq.POLLIN:
                        #string = socket.recv()
                        #check for a message, this will not block

                        message = socket.recv()

                        r = pickle.loads(message)
                        #print(   next(o)+self.name+" -> ")
                        self._iqueue.put(r)
                except Exception as e:
                    print(e)

                if(not self._oqueue.empty()):
                    next(o) 
                
            
            if self.stopped():
                socket.close()
                self.ctx.term()
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
        print("- post ->", self.name, "stopping")
        self.stop_issued.set()
        #self.ctx.term()

    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()





