import fileWorker
import os
import time
from random import random
from threading import Thread
from queue import Queue
import post
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
        self.fileWorkers = {}
        self.filePosts = {}
        #should spawn threads for each worker? that are responsible for listening on specific pipe and placing on appropriate queue
        for found in self.files_available():
            inq = Queue()
            ouq = Queue()

            self.fileWorkers[found] = {'thread': fileWorker.worker(found, inq, ouq),'input': inq, 'output': ouq}
            
            self.fileWorkers[found]['thread'].start()
            #self.fileWorkers[found]['thread'].run()

        
    def files_available(self):
        available_files = []
        for file in os.listdir("./data/"):
            if file.endswith(".h5"):
                available_files.append(file.split(".")[0])
        return(available_files)
    

a = dispatch()
while(True):
    #a.fileWorkers[found]['thread']
    for found in a.fileWorkers.keys():
        a.fileWorkers[found]['input'].put("opx")
        time.sleep(0.1)
        a.fileWorkers[found]['input'].put("clx")
        time.sleep(0.1)
        a.fileWorkers[found]['input'].put("opx")
        time.sleep(0.1)
        a.fileWorkers[found]['input'].put("clx")
#a.test()