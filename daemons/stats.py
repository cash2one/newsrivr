#!/usr/bin/env python
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
	cnt = 0
	db = None
	while not db:
		try:
			conn = pymongo.Connection(MONGOSERVER, MONGOPORT)	
			db = conn.newsrivr
		except Exception, e:
			time.sleep(2)
			cnt += 1
			if cnt>60:
				raise e
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

def getCollYoutubeTags():
	db = getDB()
	coll = db.youtubetags
	return coll

def main():
	while True:
		print datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M:%S")
		print
		print "users:", getCollUsers().find({"screen_name":{'$exists':True}}).count()
		print "tweets:", getCollUnprocessedTweets().count()
		print "drops:", getCollDrops().count()
		print "stream:", getCollStream().count()
		print "imagemd5:", getCollImageMd5s().count()
		print "youtubetags:", getCollYoutubeTags().count()
		print
		print "users:"
		for u in getCollUsers().find(sort=[("last_login",-1)]).limit(100):
			if "screen_name" in u:				
				s = "\t<b>"+u["screen_name"] + "</b> - " + str(u["id_str"]) + " - " + str(u["newsrivr_userid_md5"]) 
				if "last_login" in u:
					s += " - Last pagerefresh:"+u["last_login"] + " - pagerefreshes:"+str(u["login_count"])
				print s
				#if "agent" in u:
				#	for a in u["agent"]:
				#		s = a.split(" ")
				#		if len(s)>2:
				#			print "\t\t", s[1].replace("(", "").replace(";", ""), s[len(s)-1], s[len(s)-2]
		print
		return		
		
if __name__=='__main__':
	main()