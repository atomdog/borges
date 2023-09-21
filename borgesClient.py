import post
from queue import Queue
import time
import random
from datetime import datetime


''' 
{
    ID: <id>
    TIME: <ISOTIME>
    TYPE: <REQUEST> OR <RESPONSE>
    COMMAND: <command>
    ARGS: <args> OR None
    BODY: <content> OR None
}
'''
class borgesClient:
    def __init__(self, address):
        self.address = address
        _iqueue, _oqueue = Queue(), Queue()
        self.channel = {"channel": post.channel(address, "client", _iqueue,_oqueue), 'input': _iqueue, 'output': _oqueue}
        self.channel['channel'].start()
        self.active_requests = []
        time.sleep(1)
    def generatePacket(self):
        today = datetime.now()
        iso_date = str(today.isoformat())
        rid = hash(iso_date+str(random.random()))
        packetFrame ={
            'ID': rid,
            'TIME': iso_date,
            'TYPE': 'REQUEST',
            'COMMAND': 'None',
            'ARGS': 'None',
            'BODY': 'None'
        }
        return(packetFrame)
        
    def requestOpen(self):
        p = self.generatePacket()
        p['COMMAND'] = "opx"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])

    def requestClose(self):
        p = self.generatePacket()
        p['COMMAND'] = "clx"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])
    def requestDescription(self):
        p = self.generatePacket()
        p['COMMAND'] = "dsc"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        self.channel['output'].put(p)
        return(p['ID'])
    def requestAppendRow(self,r):
        p = self.generatePacket()
        p['COMMAND'] = "apr"
        p['ARGS'] = r
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])
    def requestGetRowAt(self, i):
        p = self.generatePacket()
        p['COMMAND'] = "gra"
        p['ARGS'] = i
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])
    def requestGetColAt(self, i):
        p = self.generatePacket()
        p['COMMAND'] = "gca"
        p['ARGS'] = i
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])
    def requestDeload(self):
        p = self.generatePacket()
        p['COMMAND'] = "dlo"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        return(p['ID'])
    def close(self):
        self.channel['channel'].stop()

    def recursive_check(self, pid):
        #if not empty, keep checking!  
        if(self.channel['input'].empty()==False):
            pack = self.channel['input'].get()
            #is this it?
            if(pack['ID'] == pid):
                #return this one
                return(pack)
            else:
                #that's not it, call again
                return(self.recursive_check(pid))
                #leave things the way you found them!
                self.channel['input'].put(pack)
        #if empty, it's not in here!     
        else:
            return(False)

    
    def check(self, pid):
        return(self.recursive_check(pid))
    


a = borgesClient("test0")
b = borgesClient("test1")
c = borgesClient("test2")

ar = a.requestOpen()
ar2 = a.requestDescription()
ari = a.requestGetRowAt(5)
arc = a.requestGetColAt('bleDeviceCount')
ar3 = a.requestClose()

time.sleep(1)
print(a.check(ar))
time.sleep(2)
print(a.check(ar2))
print(a.check(ari))
print(a.check(arc))
print(a.check(ar3))
a.close()
