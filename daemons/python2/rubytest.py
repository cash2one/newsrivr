from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
import os
import time
import hashlib
import string
import urllib.request, urllib.parse, urllib.error
import subprocess
from tempfile import *
from hn import grabContent

def getContentRuby(url, t1_name, t2_name):
    difficultsites = ['geenstijl']
    script = "/home/rabshakeh/Newsrivr/daemons/rubyreadability.rb"
    for u in difficultsites:
        if u in str(url).lower():
            script = "/home/rabshakeh/Newsrivr/daemons/rubyyreadability.rb"
    cmd = ["/usr/bin/ruby", script, t1_name, t2_name ]    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    error = p.stderr.read()
    if len(error)!=0:
        print(url)
        print(error)
    s = p.stdout.read()
    s = s.strip()
    if len(s)>0:
        print(s)
        
def getfilenames(content):
    m = hashlib.md5()
    spid=str(os.getpid())+str(time.time())
    m.update(spid)
    fnmd5 = m.hexdigest()    
    t1 = open("in-"+fnmd5+".txt", "w")
    t2 = open("out-"+fnmd5+".txt", "w")
    t1.write(content)
    t1_name = t1.name
    t2_name = t2.name
    return t1_name, t2_name

def main():
    content = open("usedforscoring.html", "r").read()    
    t1, t2 = getfilenames(content)
    getContentRuby('xx', t1, t2)
    content = open(t2, "r").read()
    #print {1:content}
    open("in.html", "w").write(content)
    #
    content = grabContent('xx', content)
    print(content)
    os.remove(t1)
    os.remove(t2)


if __name__=="__main__":
    main()