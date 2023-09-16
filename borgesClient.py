import post
from queue import Queue

class borgesClient:
    def __init__(self, address):
        self.address = address
        self.inq_z, self._oqueue = Queue(), Queue()
        self.channel = post.channel(self.address, self.inq_z, self._oqueue)
        self.channel.start()
    def requestOpen(self):
        print("Requesting Open")
        command = "opx"
        self.channel._oqueue.put(command)
    def requestClose(self, fn):
        command = "clx"
        self.channel._oqueue.put(command)
        pass
    def requestDescription(self, fn):
        command = "dsc"
        self.channel._oqueue.put(command)
        pass
    def requestAppendRow(self, fn,r):
        command = "apr"
        self.channel._oqueue.put(command)
        pass
    def requestGetRowAt(self, fn, i):
        command = "gra"
        self.channel._oqueue.put(command)
        pass
    def requestGetColAt(self, fn, i):
        command = "gca"
        self.channel._oqueue.put(command)
        pass
    def requestDeload(self, fn):
        command = "dlo"
        self.channel._oqueue.put(command)
        pass

    def close(self):
        self.channel.stop()



a = borgesClient("test0")
b = borgesClient("test1")
c = borgesClient("test2")
a.requestOpen()

a.close()
b.close()
c.close()
