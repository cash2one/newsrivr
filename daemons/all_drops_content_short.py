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
			print "no conn"
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
	print "DISABLED!!!"
	return
	cnt = 0;
	for d in getCollDrops().find(sort=[("created_at", -1)]):
		cnt += 1
		if cnt%100==0:
			print cnt
		for l in d["followed_links"]:
			for j in l["link"]:
				if "data" in j:
					del j["data"]
			html = ""
			shortened = False
			findclosetag = False
			wc = 0
			if "simplehtml" in l:
				if "<table" in l["simplehtml"]:
					html += "<div id='hide_"+d["id_str"]+"' style='display:none;'>"
					html += l["simplehtml"]
					shortened = True
				else:
					splithtml = l["simplehtml"].split(" ")
					if len(splithtml)>100:
						for i in splithtml:
							html += i + " "
							wc += 1
							if wc>50 and not shortened and not findclosetag:
								findclosetag = True								
							if findclosetag:
								if "</" in i:
									shortened = True
									findclosetag = False
									html += "<div class='contenthider' id='hide_"+d["id_str"]+"' style='display:none;'>"
				if shortened:
					html += "</div><a id='readmore_"+d["id_str"]+"' href='#' onclick='javascript:showContent(\""+d["id_str"]+"\"); return false;' style=\"float:right;\"><img src=\"/static/images/readmore.png\" alt=\"Read more\" border=\"0\" />Read more...</a>"
					l["simplehtml"] = html
					getCollDrops().save(d, safe=True)
	
if __name__ == '__main__':
	main()