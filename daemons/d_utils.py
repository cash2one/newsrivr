import os
import re
import cgi
import sys
import inspect
import calendar
import string
import time
import copy
import Image
import datetime
import urlparse
import urllib
import simplejson
import base64
import cStringIO
import pymongo
import cPickle
import traceback
import hashlib
import threading
import inspect
import portalocker
import subprocess
import feedparser
import Levenshtein
import datetime
import urlparse
import types
import pycurl
import pymongo.objectid
import multiprocessing
import socket
from time import mktime
from hn import *
from openAnything import *
from BeautifulSoup import BeautifulSoup, SoupStrainer, Comment
from html2plaintext import html2plaintext
from pymongo import ASCENDING, DESCENDING
from multiprocessing import Process, Queue
from dateutil.parser import parse
from tempfile import *
from time import gmtime, strftime
from oauthtwitter import OAuthApi
from datetime import timedelta

from oauth import (OAuthClient, OAuthConsumer, OAuthError,
						 OAuthRequest, OAuthSignatureMethod_HMAC_SHA1,
						 OAuthSignatureMethod_PLAINTEXT, OAuthToken)

STREAM_URL = "http://sitestream.twitter.com/2b/site.json"

consumer_key = "sRXKCWePy0kG43DwiG9kw"
consumer_secret = "ikO6z1CVFW4tv4NmpNo8QbhCHMQNjOq1Z7vWc25wA"

access_token = "1486311-FXaxQeHSj2TiULkZ9HRkuEJYdfU667z1GAlJ6tIY"
access_token_secret = "ol24w5utIhLzRWVb3L2E8JjKe3mjakAgo2tXfJnM9S4"

if "Darwin" in os.popen("uname").read():
	MONGOSERVER = 'localhost'
else:
	MONGOSERVER = '192.168.167.192'
MONGOPORT = 27017

socket.setdefaulttimeout(30.0)

def mailStringToAdmin(subject, str):
	try:
		if "Darwin" in os.popen("uname").read():
			return
		import mailer
		str = str.replace("\n", "<br/>").replace(" ", "&nbsp;")
		msg = mailer.GenerateMessage("NewsRivr Console Error", "noreply@newsrivr.com", "mailStringToAdmin", "info@newsrivr.com", "sysadmin@active8.nl", "sysadmin@active8.nl", subject, str, str, [])
		result = mailer.SendMessage("noreply@newsrivr.com", ["sysadmin@active8.nl"], msg)	
		return "True"
	except:
		pass
	
def mailException(e):
	try:
		import traceback
		import StringIO
		s = StringIO.StringIO()
		traceback.print_exc(file=s)
		clog(s.getvalue())
		mailStringToAdmin("mailException", s.getvalue())		
	except:
		pass
	
def clog(s):		
	s= str(s)
	print strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s
	
def unicodeToHTMLEntities(text):
	"""Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
	text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
	return text

def getDB():
	cnt = 0
	db = None
	while not db:
		try:
			conn = pymongo.Connection(MONGOSERVER, MONGOPORT)	
			db = conn.newsrivr
		except Exception, e:
			clog("no conn")
			clog(e)
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

def getCollProcessedTweets():
	db = getDB()
	coll = db.tweets_processed
	return coll

def getCollDrops():
	db = getDB()
	coll = db.drops
	return coll

def getCollImageMd5s():
	db = getDB()
	coll = db.imagemd5
	return coll

def getCollYoutubeTags():
	db = getDB()
	coll = db.youtubetags
	return coll

def getUserByMD5(md5):
    users = getCollUsers()
    sd = {"newsrivr_userid_md5": md5}
    return users.find_one(sd)

def getCollStream():
	db = getDB()
	coll = db.stream
	return coll

def getCollLists():
	db = getDB()
	coll = db.lists
	return coll

def klog(s):
	s= str(s)
	print "---------------------------"
	print s
	print "---------------------------"
	exit(1)
	
def getTimeWithMS():
	dtn = datetime.datetime.utcnow()
	before = str(calendar.timegm(dtn.timetuple()))
	after = repr(time.time())
	sa = after.split(".")
	dtnms = dtn
	if len(sa)>1:
		dtnms = before + "." + sa[1]
	return dtn, float(dtnms)
	
def checkIfRunning(cf):
	fn = str(cf).replace(".py", ".pid")
	try:
		f = open(fn, "w")
		portalocker.lock(f, portalocker.LOCK_EX|portalocker.LOCK_NB)
		timestamp = time.strftime("%m/%d/%Y %H:%M:%S\n", time.localtime(time.time()))
		f.write(timestamp)
		f.write(str(os.getpid())+"\n")
		return f
	except Exception, e:
		#traceback.print_exc(file=sys.stdout)
		return None

def driver(main, cf):
	lf = checkIfRunning(cf)
	if not lf:
		if "Darwin" in os.popen("uname").read():			
			clog(cf+" already running")
		return
	ks = str(cf).replace(".py", "")+"kill.sh"
	open(ks, "w").write("kill "+str(os.getpid())+"\nrm "+ks+"\n")
	os.system("chmod +x "+ks)
	try:
		main()
	except (KeyboardInterrupt, SystemExit):
		os.system("rm "+ks)
	except Exception, e:
		print e
		os.system("rm "+ks)
	lf.close()
	os.remove(lf.name)
	