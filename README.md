# borges - parallelized database system for python
the main purpose is to allow multiple client processes to read and write to a set of .h5 files. you probably shouldn't use this in production or really at all. i intended it to be a learning exercise. it is supposed to be used with another repo, ritual, which launches and manages this as well as all of the scripts that need access to these databases. when the two are used together you control complex workflows that may need simultaneous access to a common store of data, for example, a script which records data, a script which analyzes it, and another a server that hosts a visualization. i named it after borges because of his story "the library of babel". 

## what everything does
- post is responsible for communication
-- a post channel is a object to interact with a thread that handles ZeroMQ input and output to other processes in an asynchronous fashion 
- <b>dispatchWorker</b> is responsible for launching fileWorkers and channels
-- this routes requests from clients to the proper fileworker for execution, and then routes the responses back to the client
- fileworkers are threads which handle all I/O on files
- borgesClient is just a wrapper for a post channel and a little bit of logic that makes interacting with it in a non-async context not super miserable

## available commands
- 'opx' : opens a file
- 'clx' : closes a file. does not get rid of the copy of file in memory
- 'dsc' : returns names of columns and length row-wise
- 'apr' : appends a row to the end
- 'gra' : gets a row at index i where i is an integer
- 'gca' : gets a column at column name c where c is a string
- 'dlo' : clears the stored table from memory and also closes it