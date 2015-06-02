from __future__ import print_function
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

def main():
    #print "DISABLED!!!"
    #return
    cnt = 0
    for d in getCollDrops().find():
        if len(d["images"])>0:
            d["can_be_opened"] = True
        else:
            d["can_be_opened"] = False
            for l in d["followed_links"]:
                if "simplehtml" in l:
                    if len(l["simplehtml"].strip())!=0:
                        d["can_be_opened"] = True
                if "image" in l:
                    if len(l["image"]["src"])!=0:
                        d["can_be_opened"] = True
                if "youtube" in l:
                    d["can_be_opened"] = True
                if "vimeo" in l:
                    d["can_be_opened"] = True					
        cnt = cnt + 1
        #print d["can_be_opened"]
        if cnt%100==0:
            print(cnt)
        getCollDrops().save(d, safe=True)

if __name__ == '__main__':
    main()