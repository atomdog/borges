import fileWorker
import os
import time
from random import random
from threading import Thread
from queue import Queue
import post
import threading

# aidan m gomez
# august 2, 2023
# dispatch - 
# this program begins by finding each h5 database file the ./data/ directory
# once it has done this, it spawns in a fileworker object and starts it.
# starting the fileworker does not necessarily mean the file is open, 
# rather it just spawns a thread in charge of caring for the file and requests to it
# 
# 0. communication [ ]
# planned:
# the dispatch should begin a thread for each fileworker which enables zero-mq messaging
# each worker should have its own 'post', to prevent bottlenecking for all files.
# the dispatch should have its own post, which processes can use to gain information about available files
# the dispatch should be able to post to the workers, but other processes can also post to the worker
# notes:
#
#
# 1. intelligence [ ]
# planned:
# the dispatch should seek to optimize the memory footprint as well as availability. 
# ideally, each dispatch generates a log file detailing what has been requested of it,
# who has requested what,
# and when those requests occur
# perhaps this can permit cache-accelerated operations, or opening or closing files when needed often or not needed
# notes:
#
#
# create addresses for for different fileworkers and additional address for directory


class dispatch:
    def __init__(self):
        print("initializing dispatch...")
        self.fileWorkers = {}
        self.dispatchWorkers = {}
        #should spawn threads for each worker? that are responsible for listening on specific pipe and placing on appropriate queue
        for found in self.files_available():
            inq = Queue()
            ouq = Queue()
            inq_z = Queue()
            ouq_z = Queue()

            self.fileWorkers[found] = {'thread': fileWorker.worker(found, inq, ouq),'input': inq, 'output': ouq}
            self.fileWorkers[found]['thread'].start()

            self.dispatchWorkers[found] = worker(found, self.fileWorkers[found], False)
            self.dispatchWorkers[found].start()


            #self.fileWorkers[found]['thread'].run()
            #self.fileWorkers[found].run()
        

    def files_available(self):
        available_files = []
        for file in os.listdir("./data/"):
            if file.endswith(".h5"):
                available_files.append(file.split(".")[0])
        return(available_files)
    



class worker(threading.Thread):
    # dispatch worker class
    # as an argument, takes 
    #   name
    #       the name of the dispatch worker which also serves as the channel address
    #   fw
    #       the fileworker which this dispatch worker will manage & operate
    #   sig
    #       a signal variable for control from the main thread
    #
    # 

    def __init__(self, name, fw, sig):


        print("spawning dispatch worker for " + name)

        threading.Thread.__init__(self)
        self.stop_issued = threading.Event()
        inq_z, ouq_z = Queue(), Queue()
        self.name = name
        self.managed_fw = fw
        self.sig = sig
        self.channel = post.channel(self.name, inq_z, ouq_z)
        self.channel.start()
        self.work = Queue()
        pass
    #thread methods
    #thread runtime
    def run(self):
        try:
            breaker=False
            #enter into thread runtime
            #begin passive reception. this should listen for any updates on the channel and place them on the inbound queue where we can get them at our leisure.
            #inboundRequest = self.channel.receive()
            #print("dispatch worker, channel: ", self.name, " has launched passive reception")
            while(not breaker):
                #do while breaker is not tripped by one of the kill conditions
                #if the request queue is not empty

                #get any new requests
                
                #if(self.channel.getIQ()):
                    #print("ok")
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
        print("dispatch worker ", self.name, " stopping")
        self.closeFile()
        self.stop_issued.set()
    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()

    

a = dispatch()

#a.test()