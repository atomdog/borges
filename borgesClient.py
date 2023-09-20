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

    def requestClose(self):
        p = self.generatePacket()
        p['COMMAND'] = "clx"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        pass
    def requestDescription(self):
        p = self.generatePacket()
        p['COMMAND'] = "dsc"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        self.channel['output'].put(command)
        pass
    def requestAppendRow(self,r):
        p = self.generatePacket()
        p['COMMAND'] = "apr"
        p['ARGS'] = r
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        pass
    def requestGetRowAt(self, i):
        p = self.generatePacket()
        p['COMMAND'] = "gra"
        p['ARGS'] = i
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        pass
    def requestGetColAt(self, i):
        p = self.generatePacket()
        p['COMMAND'] = "gca"
        p['ARGS'] = i
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        pass
    def requestDeload(self):
        p = self.generatePacket()
        p['COMMAND'] = "dlo"
        self.channel['output'].put(p)
        self.active_requests.append(p['ID'])
        pass
    def close(self):
        self.channel['channel'].stop()



a = borgesClient("test0")
b = borgesClient("test1")
c = borgesClient("test2")
a.requestOpen()
b.requestOpen()
c.requestOpen()
