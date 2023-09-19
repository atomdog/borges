import post
from queue import Queue
import time
class borgesClient:
    def __init__(self, address):
        self.address = address
        _iqueue, _oqueue = Queue(), Queue()
        self.channel = {"channel": post.channel(address, "client", _iqueue,_oqueue), 'input': _iqueue, 'output': _oqueue}
        self.channel['channel'].start()
        time.sleep(1)
    def requestOpen(self):
        print("Requesting Open")
        command = "opx"
        self.channel['output'].put(command)
    def requestClose(self, fn):
        command = "clx"
        self.channel['output'].put(command)
        pass
    def requestDescription(self, fn):
        command = "dsc"
        self.channel['output'].put(command)
        pass
    def requestAppendRow(self, fn,r):
        command = "apr"
        self.channel['output'].put(command)
        pass
    def requestGetRowAt(self, fn, i):
        command = "gra"
        self.channel['output'].put(command)
        pass
    def requestGetColAt(self, fn, i):
        command = "gca"
        self.channel['output'].put(command)
        pass
    def requestDeload(self, fn):
        command = "dlo"
        self.channel['output'].put(command)
        pass
    def close(self):
        self.channel['channel'].stop()



a = borgesClient("test0")
b = borgesClient("test1")
c = borgesClient("test2")
a.requestOpen()
b.requestOpen()
c.requestOpen()
