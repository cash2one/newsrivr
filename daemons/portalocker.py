# portalocker.py - Cross-platform (posix/nt) API for flock-style file locking.
#                  Requires python 1.5.2 or better.
"""Cross-platform (posix/nt) API for flock-style file locking.

Synopsis:

   import portalocker
   file = open("somefile", "r+")
   portalocker.lock(file, portalocker.LOCK_EX)
   file.seek(12)
   file.write("foo")
   file.close()

If you know what you're doing, you may choose to

   portalocker.unlock(file)

before closing the file, but why?

Methods:

   lock( file, flags )
   unlock( file )

Constants:

   LOCK_EX
   LOCK_SH
   LOCK_NB

Exceptions:

    LockException

Notes:

For the 'nt' platform, this module requires the Python Extensions for Windows.
Be aware that this may not work as expected on Windows 95/98/ME.

History:

I learned the win32 technique for locking files from sample code
provided by John Nielsen <nielsenjf@my-deja.com> in the documentation
that accompanies the win32 modules.

Author: Jonathan Feinberg <jdf@pobox.com>,
        Lowell Alleman <lalleman@mfps.com>
Version: $Id: portalocker.py 5474 2008-05-16 20:53:50Z lowell $

"""


__all__ = [
    "lock",
    "unlock",
    "LOCK_EX",
    "LOCK_SH",
    "LOCK_NB",
    "LockException",
]

import os

class LockException(Exception):
    # Error codes:
    LOCK_FAILED = 1

if os.name == 'posix':
    import fcntl
    LOCK_EX = fcntl.LOCK_EX
    LOCK_SH = fcntl.LOCK_SH
    LOCK_NB = fcntl.LOCK_NB
else:
    raise RuntimeError, "PortaLocker only defined for nt and posix platforms"

if os.name == 'posix':
    def lock(file, flags):
        try:
            fcntl.flock(file.fileno(), flags)
        except IOError, exc_value:
            #  IOError: [Errno 11] Resource temporarily unavailable
            if exc_value[0] == 11:
                raise LockException(LockException.LOCK_FAILED, exc_value[1])
            else:
                raise
    
    def unlock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

if __name__ == '__main__':
    from time import time, strftime, localtime
    import sys
    import portalocker

    log = open('log.txt', "w")
    try:
        portalocker.lock(log, portalocker.LOCK_EX|LOCK_NB)
        timestamp = strftime("%m/%d/%Y %H:%M:%S\n", localtime(time()))
        log.write( timestamp )
        
        print "Wrote lines. Hit enter to release lock."
        dummy = sys.stdin.readline()
        
        log.close()        
    except Exception, e:
        print "already running"

    