import fileWorker
import os
import time
from random import random
from threading import Thread
from queue import Queue

class dispatch:
    def __init__(self):
        self.fileWorkers = {}


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