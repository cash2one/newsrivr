#!/usr/bin/env python
from __future__ import print_function
import pymongo
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

def getCollImageMd5s():
    db = getDB()
    coll = db.imagemd5
    return coll

def main():
	print("users:", getCollUsers().count())
	print("tweets:", getCollUnprocessedTweets().count())
	print("drops:", getCollDrops().count())
	print("imagemd5:", getCollImageMd5s().count())	
	#getCollUsers().drop()
	getCollUnprocessedTweets().drop()
	getCollDrops().drop()
	getCollImageMd5s().drop()
	print("users:", getCollUsers().count())
	print("tweets:", getCollUnprocessedTweets().count())
	print("drops:", getCollDrops().count())
	print("imagemd5:", getCollImageMd5s().count())
	
if __name__=='__main__':
	main()
	
	print("done")
