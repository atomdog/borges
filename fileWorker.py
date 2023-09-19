import numpy as np
import tables
import matplotlib.pyplot as plt
import os
from datetime import datetime
import shutil
import json
import pandas as pd

import sys
import subprocess
import random
import time
import threading
import queue
import os


class worker(threading.Thread):
    def __init__(self, filename, iq, oq):
        print("- fileworker -> spawning worker for " + filename)
        self.filename = filename
        self.open = False
        self.h5file = None
        self.table = None


        threading.Thread.__init__(self)
        
        self._iqueue = iq
        self._oqueue = oq

        self.stop_issued = threading.Event()

        #opx, clx, dsc, apr, gra, gca, dlo
        #open, close, describe, append row, get row at, get column at, deload (close file)
        self.control = {     "opx": lambda self: self.openFile(),
                             "clx": lambda self: self.closeFile(),
                             "dsc": lambda self: self.describeFile(),
                             "apr": lambda self, r: self.appendRow(r),
                             "gra": lambda self, i: self.getRowAt(i),
                             "gca": lambda self, i: self.getColAt(i),
                             "dlo": lambda self: self.deload()}
        
        pass

    # file io functions

    def fileExists(self):
        file_exists = os.path.exists("data/"+self.filename+".h5")
        return(file_exists)
    
    def openFile(self):
        print("- fileworker -> worker opening " + self.filename)
        self.h5file = tables.open_file("data/"+self.filename+".h5", mode="a", title="constructedlog")
        self.table = self.h5file.root.group0.table0
        self.open = True
        return(True)
    
    def closeFile(self):
        print("- fileworker -> worker closing " + self.filename)
        if(self.table is not None):
            self.table.flush()
            self.h5file.close()
        self.open = False
        return(True)
    
    def describeFile(self):
        names = self.table.coldescrs.keys()
        rowCount = 0
        columnIDs = []
        for name in names:
            columnIDs.append(name)
        rowCount = len(self.table)
        return(columnIDs, rowCount)
    
    def appendRow(self, new_row):
        r = self.table.row
        for key in new_row:
            r[key] = new_row[key]
        r.append()
        self.table.flush()
        return(True)

    def getRowAt(self, index):
        names = self.table.coldescrs.keys()
        selected_row = self.table.read(index, index+1)
        q = {}
        for column_name in names:
            c = selected_row[column_name]
            if(isinstance(c, (bytes, bytearray))):
                q[column_name]=c.decode()
            else:
                q[column_name]=c
        self.table.flush()
        return(q)
    
    def getColAt(self, index):
        names = self.table.coldescrs.keys()
        q = self.table.col(index)
        self.table.flush()
        return(q)

    def deload(self):
        if(self.open == True):
            self.closeFile()
        self.h5file = None
        self.table = None
        return(True)

    def snapshot(self):
        if(self.open):
            self.closeFile()
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        shutil.copy("data/"+self.filename+".h5", "data/snapshot_"+self.filename+"-" + dt_string + ".h5")
        return(True)


    #thread methods

    #thread runtime
    def run(self):
        try:
            breaker=False
            #enter into thread runtime
            while(not breaker):
                #do while breaker is not tripped by one of the kill conditions
                #if the request queue is not empty
                if(not self._iqueue.empty()):
                    args = None
                    #get the controlcode passed to the thread    
                    cflow = self._iqueue.get()
                    #if a list w/ arguments is passed, split and run with arguments
                    if isinstance(cflow, list):
                        controlflow, args = cflow[0], cflow[1]
                    else:
                        controlflow = cflow
                    try:
                        if(args is not None):
                            o = self.control[controlflow](self, args)
                        else:
                            o = self.control[controlflow](self)
                        #place on output queue
                        self._oqueue.put(o)
                        time.sleep(0.1)
                    except Exception as e:
                        self._oqueue.put(e)
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
        print("- fileworker -> worker ", self.filename, " stopping")
        self.closeFile()
        self.stop_issued.set()
    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()

    

def constructLog(schema, filename):
    logObj = consLog
    constructedColumns = {}
    for x in range(0, len(schema)):
        column_id = schema[x]['id']
        column_type = schema[x]['type']
        if(column_type=='text'):
            logObj.columns[column_id]=tables.StringCol(1024)
        elif(column_type=='int'):
            logObj.columns[column_id]=tables.Float64Col()

    h5file = tables.open_file("data/"+filename+".h5", mode="w", title="constructedlog")
    group = h5file.create_group("/", 'group0', filename+" first group")
    table = h5file.create_table(group, 'table0', logObj, filename+" first table")
    table.flush()
    h5file.close()
    return(1)









