import sys
import subprocess
import random
import time
import threading
import queue
import os
#thanks to:
#https://www.stefaanlippens.net/python-asynchronous-subprocess-pipe-reading/
#for source material to modify

#this is an extension of the threading.Thread class
class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        #assert isinstance(queue, queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
        #for whatever reason the thread does not join even when polling the process
        #returns 0
        #as a result a stop event must be added which enables the thread to be quit 
        #when the poll returns 0, ie the process is completed
        self.stop_issued = threading.Event()
        
    def run(self):

        '''
        Old run() function in case I broke something!

        try:
            for line in iter(self._fd.readline, ''):
                self._queue.put(line)
                if self.stopped():
                    return
        except Exception as e:
            print(e)
            return(-1)
        '''
        #The body of the thread: read lines and put them on the queue.
        try:
            breaker=False
            while(not breaker):
                if(self._fd.closed == False):
                    line = self._fd.readline()
                    self._queue.put(line)
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
                
    def eof(self):
        #Check whether there is no more content to expect.
        return not self.is_alive() and self._queue.empty()

    def stop(self):
        #set stop event
        self.stop_issued.set()
    
    def stopped(self):
        #check if thread class event has been set
        return self.stop_issued.is_set()



#start, pass <LIST:command> or <LIST:command>,<OS.workingdirectory>, 
#return process, queue, reader objects
def start(*args):
    if len(args) == 1:
        command = args[0]
        wd = os.getcwd()
    elif len(args) == 2:
        command = args[0]
        wd = args[1]

    breaker = False
    # Launch the command as subprocess.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, cwd= wd)

    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = queue.Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()

    stderr_queue = queue.Queue()
    stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
    stderr_reader.start()
    
    processthreadbundle = {'process': process, 
                       'stdout_queue': stdout_queue, 
                       'stdout_reader': stdout_reader,
                       'stderr_queue': stderr_queue, 
                       'stderr_reader': stdout_reader}
    
    return(processthreadbundle)

def status(processthreadbundle):
    stdout_reader = processthreadbundle['stdout_reader']
    stderr_reader = processthreadbundle['stdout_reader']
    process = processthreadbundle['process']
    return(process.poll())

def kill(processthreadbundle):
    stdout_reader = processthreadbundle['stdout_reader']
    stderr_reader = processthreadbundle['stdout_reader']
    process = processthreadbundle['process']

    #kill process if it's not already dead
    process.kill()
    stdout_reader.stop()
    stdout_reader.join()
    
    assert stdout_reader.is_alive() == False
    #.stop() call circumvents zombie thread bug
    stderr_reader.stop()
    stderr_reader.join()
    assert stderr_reader.is_alive() == False

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()
    #print(process.poll())
    #print("> killed ", processthreadbundle['process'])
    return(process.poll())

def readIn(processthreadbundle):
    stdout_reader = processthreadbundle['stdout_reader']
    stderr_reader = processthreadbundle['stdout_reader']
    process = processthreadbundle['process']
    stdout_queue = processthreadbundle['stdout_queue']
    stderr_queue = processthreadbundle['stderr_queue']

    output, error = None, None
    if (not stdout_reader.eof() or not stderr_reader.eof()):
        # Show what we received from standard output.
        if not stdout_queue.empty():
            line = stdout_queue.get()
            if(line.decode()!=''):
                #print('Received line on standard output: ' + repr(line.decode()))
                output = repr(line.decode())
        if not stderr_queue.empty():
            line = stderr_queue.get()
            if(line.decode()!=''):
                #print('Received line on standard error: ' + repr(line.decode()))
                error = repr(line.decode())
        # Sleep a bit before asking the readers again.
        time.sleep(.1)
        poll = process.poll()    
        return(output, error)
        

#source material code no longer used
def consume(command):
    '''
    Example of how to consume standard output and standard error of
    a subprocess asynchronously without risk on deadlocking.
    '''
    breaker = False
    # Launch the command as subprocess.
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = queue.Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()
    stderr_queue = queue.Queue()
    stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
    stderr_reader.start()

    # Check the queues if we received some output (until there is nothing more to get).
    while (not stdout_reader.eof() or not stderr_reader.eof()) and breaker is False:
        # Show what we received from standard output.
        while not stdout_queue.empty():
            line = stdout_queue.get()
            if(line.decode()!=''):
                print('Received line on standard output: ' + repr(line.decode()))
            #print('Received line on standard output: ' + repr(line))
            #print(line.read())

        # Show what we received from standard error.
        while not stderr_queue.empty():
            line = stderr_queue.get()
            if(line.decode()!=''):
                print('Received line on standard error: ' + repr(line.decode()))
            #print(line.read())

        # Sleep a bit before asking the readers again.
        time.sleep(.1)
        poll = process.poll()
        if poll is None:
            pass
        else:
            #print(poll)
            # Let's be tidy and join the threads we've started.
            breaker = True
            #.stop() call circumvents zombie thread bug
            stdout_reader.stop()
            stdout_reader.join()

            #.stop() call circumvents zombie thread bug
            stderr_reader.stop()
            stderr_reader.join()
             

            # Close subprocess' file descriptors.
            process.stdout.close()
            process.stderr.close()
            
            #print("breaker is true")
#source material code no longer used
def produce(items=10):
    '''
    Dummy function to randomly render a couple of lines
    on standard output and standard error.
    '''
    for i in range(items):
        output = random.choice([sys.stdout, sys.stderr])
        output.write('Line %d on %s\n' % (i, output))
        output.flush()
        time.sleep(random.uniform(.1, 1))

if __name__ == '__main__':
    processthreadbundle_a = start(['python3', '-u', 'dummy.py'])
    processthreadbundle_b = start(['python3', '-u', 'dummy2.py'])
    for x in range(0, 10):
        time.sleep(1)
        readIn(processthreadbundle_a)
        readIn(processthreadbundle_b)


    kill(processthreadbundle_a)
    time.sleep(2)
    for x in range(0, 10):
        time.sleep(1)
        readIn(processthreadbundle_b)
    kill(processthreadbundle_b)

