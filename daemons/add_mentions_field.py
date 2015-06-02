from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import re
import os
import time
import pymongo
import datetime
from pymongo import ASCENDING, DESCENDING

if "Darwin" in os.popen("uname").read():
	MONGOSERVER = 'localhost'
else:
	MONGOSERVER = '192.168.167.192'
	
MONGOPORT = 27017

def getDB():
    conn = None
    while not conn:
        try:
            conn = pymongo.Connection(MONGOSERVER, MONGOPORT)
        except:
            time.sleep(1)
            print("no conn")
    db = conn.newsrivr
    return db

def getCollUsers():
    db = getDB()
    coll = db.users
    return coll

def getCollUnprocessedTweets():
    db = getDB()
    coll = db.tweets
    return coll

def getCollDrops():
    db = getDB()
    coll = db.drops
    return coll

def getCollStream():
    db = getDB()
    coll = db.stream
    return coll

def getCollImageMd5s():
    db = getDB()
    coll = db.imagemd5
    return coll

def retMentions(text):
    l = []
    text = re.sub(r'(?<![a-zA-Z-_])@([a-zA-Z0-9_-]+)', lambda x: l.append(x.group().strip()), text)
    return l

def main():
    
    
    #print "DISABLED!!!"
    #return
    cnt = 0
    for d in getCollDrops().find():
        d["mentions"] = retMentions(d["org_content"])
        cnt = cnt + 1
        #print d["can_be_opened"]
        if cnt%100==0:
            print(cnt)
        getCollDrops().save(d, safe=True)

if __name__ == '__main__':
    main()
