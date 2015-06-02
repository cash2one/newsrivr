#!/usr/bin/env python
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
	conn = pymongo.Connection(MONGOSERVER, MONGOPORT)	
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
	ids = set()
	cnt = 0
	for i in getCollDrops().find():
		ids.add(i["id_str"])
		cnt += 1
	print(len(ids), cnt)
	return

	cnt2 = 0
	for id in ids:
		cd = None
		for d in getCollDrops().find({"id_str":id}):
			if type(d["newsrivr_userid_md5"])!=type([]):
				if not cd:
					cd = d
					cd["newsrivr_userid_md5"] = [cd["newsrivr_userid_md5"]]
				else:
					cd["newsrivr_userid_md5"].append(d["newsrivr_userid_md5"])
					getCollDrops().remove({"id_str":id}, safe=True)
				cnt2 += 1
				if cnt2%1000==0:
					print(cnt2)
					time.sleep(1)
		getCollDrops().save(cd, safe=True)
			
	
		
if __name__=='__main__':
	main()
	print("done")