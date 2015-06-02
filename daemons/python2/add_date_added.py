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
		d["added_at"] = d["created_at"]#dnow = datetime.datetime.utcnow()
		cnt = cnt + 1
		if cnt%100==0:
			print(cnt)
		getCollDrops().save(d, safe=True)

if __name__ == '__main__':
	main()