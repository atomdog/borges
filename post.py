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
        self.sender = self.ctx.socket(zmq.PUSH)
        
        self.sender.connect('ipc:///tmp/'+self.name+'_'+self.outgoing_label+'.pipe')
        print("- post -> opened outbound channel", self.name)
        while(self.stop_issued.is_set() is False):
            try: 
                if(self._oqueue.empty() == False):
                    msg = self._oqueue.get()
                    print("- post -> outbound on "+self.name+" -> ")
                    msg = pickle.dumps(msg)
                    try:
                        self.sender.send(msg)
                    except Exception as e:
                        print(e)
                    #print(msg)
            except:
                #self.sender.close()
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
                        print("- post -> inbound on "+self.name+" -> ")
                        r = pickle.loads(message)
                        #print(   next(o)+self.name+" -> ")
                        self._iqueue.put(r)
                except Exception as e:
                    print(e)
                    break

                if(not self._oqueue.empty()):
                    next(o) 
            
            if self.stopped():
                print("- post - > channel ",self.name, "terminating...")
                sen = self.sender.close(linger=0)
                inc = socket.close(linger=0)
                ctc = self.ctx.term()
                ctc2 = self.ctx.destroy()
                return(-1)
                
                
            else:
                self.stop()
                breaker=True
        except Exception as e:
            print(e)
            self.stop()
        return(-1)

    
    def stop(self):
        #set stop event
        self.stop_issued.set()
        #self.ctx.term()
        return(-1)

    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()





