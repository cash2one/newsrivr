#!/usr/bin/env python
import os
import time
import pymongo
import pymongo.objectid

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
		except Exception, e:
			time.sleep(1)
			print "no conn", e
	db = conn.newsrivr
	return db

def getCollUsers():
	db = getDB()
	coll = db.users
	return coll

def getCollDrops():
	db = getDB()
	coll = db.drops
	return coll

def clog(s):
	print str(s)
	
def main():
	if "Darwin" not in os.popen("uname").read():
		print "this can't be run on a server dude"
		return
	print "DELETE USERS !!!"
	import random
	ri = random.randint(100,1000)
	print ri
	keepdropuser = []
	deletedropuser = []
	richeck = raw_input("Check: wat is het nummer: ")	
	if ri==int(richeck):
		print "ok, deleting"
		for u in getCollUsers().find():
			if "screen_name" in u:
				if "rabshakeh" in u["screen_name"] or "Scobleizer" in u["screen_name"]:
					print u["screen_name"]
					keepdropuser.append(u["newsrivr_userid_md5"])
				else:
					deletedropuser.append(u["newsrivr_userid_md5"])
					getCollUsers().remove({"_id":pymongo.objectid.ObjectId(u["_id"])})
			else:
				getCollUsers().remove({"_id":pymongo.objectid.ObjectId(u["_id"])})
		cnt = getCollDrops().find().count()
		getCollDrops().remove({"newsrivr_userid_md5":{"$nin":keepdropuser}})
		return
	else:
		print "bye"

def main2():
	for d in getCollDrops().find():
		if len(d["newsrivr_userid_md5"])>1:
			print d["newsrivr_userid_md5"]
		if len(d["newsrivr_userid_md5"])==0:
			print "gek"
			exit(1)
			
if __name__ == '__main__':
	main()