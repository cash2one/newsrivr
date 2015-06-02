"""
- bug show background checkbox
- archive of tweets
- rss of that archive
"""

import re
import os
import datetime
import hashlib
import pymongo
import oauth
import httplib
import time
import datetime
import base64
import simplejson
import cgi
import commands
import mailer
import sys
import urlparse
import traceback
import multiprocessing
import twitter
import random
import cStringIO
import Image
import calendar
from pymongo import objectid
from django.template import loader, Context, Template
from BeautifulSoup import BeautifulSoup, Comment
from time import mktime
from dateutil.parser import parse
from pymongo.objectid import ObjectId
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django import forms
from django.http import *
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.html import urlize, escape
from twitter_utils import *
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, InvalidPage
from django.template.defaultfilters import escapejs
from BeautifulSoup import BeautifulSoup, SoupStrainer, Comment
from django.utils.text import capfirst

def mailStringToAdmin(subject, str):
	try:
		if "Darwin" in os.popen("uname").read():
			return
		import mailer
		str = str.replace("\n", "<br/>").replace(" ", "&nbsp;")
		msg = mailer.GenerateMessage("NewsRivr website message", "noreply@newsrivr.com", "mailStringToAdmin", "info@newsrivr.com", "erik@active8.nl", "erik@active8.nl", subject, str, str, [])
		result = mailer.SendMessage("noreply@newsrivr.com", ["erik@active8.nl"], msg)	
		return "True"
	except Exception, e:
		clog("mailStringToAdmin:"+str(e))
	
def getTimeWithMS():
	dtn = datetime.datetime.utcnow()
	before = str(calendar.timegm(dtn.timetuple()))
	after = repr(time.time())
	sa = after.split(".")
	dtnms = dtn
	if len(sa)>1:
		dtnms = before + "." + sa[1]
	return dtn, float(dtnms)
	
def latin1_to_ascii (unicrap):
	xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
		0xc6:'Ae', 0xc7:'C',
		0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
		0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
		0xd0:'Th', 0xd1:'N',
		0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
		0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
		0xdd:'Y', 0xde:'th', 0xdf:'ss',
		0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
		0xe6:'ae', 0xe7:'c',
		0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
		0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
		0xf0:'th', 0xf1:'n',
		0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
		0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
		0xfd:'y', 0xfe:'th', 0xff:'y',
		0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
		0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
		0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
		0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
		0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
		0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
		0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 
		0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
		0xd7:'*', 0xf7:'/'
		}
	r = ''
	for i in unicrap:
		if xlate.has_key(ord(i)):
			r += xlate[ord(i)]
		elif ord(i) >= 0x80:
			pass
		else:
			r += str(i)
	return r

def toUTF8(data):
	try:
		data = data.encode("utf-8")
	except:
		data = latin1_to_ascii(data)
	return data

osname = None
def clog(s):
	global osname
	if not osname:
		osname = os.popen("uname").read()
	if "Darwin" in osname:
		s= str(s)
		print '\033[%93m'+s+'\033[%0m'

def getDB():
	conn = pymongo.Connection(settings.MONGOSERVER, settings.MONGOPORT)	
	db = conn.newsrivr
	return db

def getCollUsers():
	db = getDB()
	coll = db.users
	return coll

def getCollMessages():
	db = getDB()
	coll = db.messages
	return coll

def getCollDrops():
	db = getDB()
	coll = db.drops
	return coll

def getCollProcessedTweets():
	db = getDB()
	coll = db.tweets_processed
	return coll

def getCollUnprocessedTweets():
	db = getDB()
	coll = db.tweets
	return coll

def getCollImageMd5s():
	db = getDB()
	coll = db.imagemd5
	return coll

def getCollYoutubeTags():
	db = getDB()
	coll = db.youtubetags
	return coll

def deleteDrops(dropids):
	for did in dropids:
		getCollDrops().remove({"id_str":did}, safe=True)
		getCollYoutubeTags().remove({"id_str":did}, safe=True)
		getCollImageMd5s().remove({"id_str":did}, safe=True)
		getCollProcessedTweets().remove({"id_str":did}, safe=True)

def getUserByMD5(md5):
	users = getCollUsers()
	sd = {"newsrivr_userid_md5": md5}
	return users.find_one(sd)	

def createAccount():
	user = {}
	user["date_created"] = parse(commands.getoutput("date"))
	users = getCollUsers()		 
	userid = users.insert(user)
	newsrivr_userid_md5 = hashlib.md5(str(userid)).hexdigest()
	user["newsrivr_userid_md5"] = newsrivr_userid_md5
	users.save(user)
	return user
	
def getCurrentUser(request):
	if not request.COOKIES.has_key("newsrivr_userid_md5"):
		clog("creating account")
		return createAccount()
	clog("found an account")
	cu = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
	if not cu:
		clog("cookie found but no user creating account")
		cu = createAccount()		
	return cu
	
def setCookie(response, key, value, expire=None):
	if expire is None:
		max_age = 365*24*60*60  #one year
	else:
		max_age = expire
	expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
	response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

def striptags(data):
	soup = BeautifulSoup(data)
	for tag in soup.findAll(True):
		tag.hidden = True
	data = soup.renderContents()
	soup = BeautifulSoup(data)
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]
	return soup.renderContents()

def ismobile(request):
	is_mobile = False;

	if request.META.has_key('HTTP_USER_AGENT'):
		user_agent = request.META['HTTP_USER_AGENT']

		# Test common mobile values.
		pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|pda|mobile|mini|palm|netfront)"
		prog = re.compile(pattern, re.IGNORECASE)
		match = prog.search(user_agent)

		if match:
			is_mobile = True;
		else:
			# Nokia like test for WAP browsers.
			# http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

			if request.META.has_key('HTTP_ACCEPT'):
				http_accept = request.META['HTTP_ACCEPT']

				pattern = "application/vnd\.wap\.xhtml\+xml"
				prog = re.compile(pattern, re.IGNORECASE)

				match = prog.search(http_accept)

				if match:
					is_mobile = True

		if not is_mobile:
			# Now we test the user_agent from a big list.
			user_agents_test = ("w3c ", "acs-", "alav", "alca", "amoi", "audi",
								"avan", "benq", "bird", "blac", "blaz", "brew",
								"cell", "cldc", "cmd-", "dang", "doco", "eric",
								"hipt", "inno", "ipaq", "java", "jigs", "kddi",
								"keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
								"maui", "maxo", "midp", "mits", "mmef", "mobi",
								"mot-", "moto", "mwbp", "nec-", "newt", "noki",
								"xda",  "palm", "pana", "pant", "phil", "play",
								"port", "prox", "qwap", "sage", "sams", "sany",
								"sch-", "sec-", "send", "seri", "sgh-", "shar",
								"sie-", "siem", "smal", "smar", "sony", "sph-",
								"symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
								"upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
								"wapi", "wapp", "wapr", "webc", "winw", "winw",
								"xda-", )

			test = user_agent[0:4].lower()
			if test in user_agents_test:
				is_mobile = True
	return is_mobile

class mailDrop():
	def __init__(self, user_md5, drop_id, reply_to, tomail, body):
		self.drop_id =drop_id
		self.reply_to = reply_to
		self.tomail = tomail
		self.body = body
		self.user_md5 = user_md5
	def run(self):
		data = None
		data = getCollDrops().find_one({"_id": objectid.ObjectId(self.drop_id)})	
		if not data:
			clog("mailDrop: can't find drop")
			return
		user = getUserByMD5(self.user_md5)
		if not user:
			clog("mailDrop: can't find user")
			return			
		name = user["twitter_credentials"]["name"]
		if not name:
			name = user["twitter_credentials"]["screen_name"]
		subject = striptags(data["org_content"])		
		tmpl_html_body = loader.get_template("drop_share_html.html")
		tmpl_plain_body = loader.get_template("drop_share_txt.html")
		
		for l in data["followed_links"]:
			html = ""
			if "simplehtml" in l:			
				soup = BeautifulSoup(l["simplehtml"])
				for tag in soup.findAll(True):
					if tag.has_key("id"):
						if "nr_hide_" in str(tag["id"]):
							tag.hidden = True
						if "nr_readmore_" in str(tag["id"]):
							tag.extract()
				l["simplehtml"] = soup.renderContents()
		cdict = {"data": data, "body":self.body, "subject":subject, "user": user, "name":name, "datum": data["created_at"]}
		if "retweet_created_at" in data:
			cdict["retweet_datum"] = data["retweet_created_at"]
		c = Context(cdict)			
		html_content = tmpl_html_body.render(c)
		plain_content = tmpl_plain_body.render(c)
		msg = mailer.GenerateMessage("NewsRivr", "noreply@newsrivr.com", name, self.reply_to, self.tomail, self.tomail, subject, html_content, plain_content, [])
		result = mailer.SendMessage("noreply@newsrivr.com", [self.tomail], msg)	
		return "True"

def sharedatauser(request):
	result = False	
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:		
			data = request.POST				
			body = data["body"]
			email_clear_history = data["email_clear_history"]
			if "share_data" not in user:
				user["share_data"] = {}					
			if "previous_emails" not in user["share_data"]:
				user["share_data"]["previous_emails"] = []
			user["share_data"]["to"] = data["to"]
			user["share_data"]["reply"] = data["reply"]
			if data["cc"]=="false":
				user["share_data"]["cc"] = False
			else:
				user["share_data"]["cc"] = True
			email_pattern = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')
			if data["email_clear_history"]=="true":
				user["share_data"]["previous_emails"] = []				
			if data["email_add_used_addresses"]=="true":
				user["share_data"]["previous_emails"].append(data["to"])
				s = set()
				for email in user["share_data"]["previous_emails"]:					
					if email_pattern.match(email):
						s.add(email)
				user["share_data"]["previous_emails"] = list(s)
			getCollUsers().save(user, safe=True)
			result = True
			reply_to = user["share_data"]["reply"]
			if len(reply_to)==0:
				reply_to = "noreply@newsrivr.com"
			checkedemails = []
			emaillist = user["share_data"]["to"].split(",")
			for email in emaillist:
				if email_pattern.match(email.strip()):
					checkedemails.append(email.strip())
			for email in checkedemails:
				md = mailDrop(request.COOKIES["newsrivr_userid_md5"], data["_id"], reply_to, email, data["body"]);
				md.run()
			if user["share_data"]["cc"]:
				md = mailDrop(request.COOKIES["newsrivr_userid_md5"], data["_id"], reply_to, user["share_data"]["reply"], data["body"]);
				md.run()						
	context = {"json": simplejson.dumps(result)}
	return direct_to_template(request, "raw.html", context)				

def favorite_action(request):
	result = False
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:		
			data = request.POST
			access_token = dict(urlparse.parse_qsl(user["access_token"]))				
			api = twitter.Api(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
			if data.has_key("id_str"):
				s = twitter.Status(id=data["id_str"])
				if data["action"]=="destroy":
					try:
						api.DestroyFavorite(s)
					except twitter.TwitterError, e:
						d = getCollDrops().find_one({"retweet_id_str":data["id_str"]})
						retweet = False
						if d:
							if "favorites" in d:
								if user["id_str"] in d["favorites"]:
									retweet = True                                    
						if not d or not retweet:
							d = getCollDrops().find_one({"id_str":data["id_str"]})
						if d:
							if "favorites" in d:
								if int(user["id_str"]) in d["favorites"]:
									d["favorites"].remove(int(user["id_str"]))
									favs = []
									for i in d["favorites"]:
										favs.append(int(i))
									d["favorites"] = list(set(favs))
									clog("destroy favorite")
								getCollDrops().save(d, safe=True)          
				elif data["action"]=="create":
					try:
						api.CreateFavorite(s)
					except twitter.TwitterError, e:
						clog(e)
						api.DestroyFavorite(s)
						api.CreateFavorite(s)
		result = True		
	context = {"json": simplejson.dumps(result)}
	return direct_to_template(request, "raw.html", context)				
		
def tweetReply(request):
	result = False
	clog("tweetReply")
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:
			data = request.POST
			access_token = dict(urlparse.parse_qsl(user["access_token"]))				
			api = twitter.Api(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
			if data.has_key("id_str"):
				clog(data["text"])
				clog(data["id_str"])
				api.PostUpdate(data["text"], data["id_str"])
				result = True						
	context = {"json": simplejson.dumps(result)}						
	return direct_to_template(request, "raw.html", context)							

def tweet(request):
	result = False
	clog("tweetReply")
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:
			data = request.POST
			access_token = dict(urlparse.parse_qsl(user["access_token"]))				
			api = twitter.Api(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
			if data.has_key("text"):
				clog(data["text"])
				api.PostUpdate(data["text"])
				result = True						
	context = {"json": simplejson.dumps(result)}						
	return direct_to_template(request, "raw.html", context)							

def retweet(request):
	result = False
	clog("retweeting")
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:
			data = request.POST
			access_token = dict(urlparse.parse_qsl(user["access_token"]))				
			api = twitter.Api(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
			if data.has_key("id_str"):
				if data["action"]=="create":
					clog("retweet")
					url = 'http://api.twitter.com/1/statuses/retweet/%s.json' % data["id_str"]
					json = api._FetchUrl(url, post_data={'id': data["id_str"]})
					data = simplejson.loads(json)
					if data:
						result = True
				elif data["action"]=="destroy":
					clog("undo retweet")
					d = getCollDrops().find_one({"retweet_id_str":data["id_str"], "screen_name":user["screen_name"]})
					if d:
						clog(d["id_str"])
						api.DestroyStatus(d["id_str"])	 
					else:
						clog("can't find drop to undo retweet")
	context = {"json": simplejson.dumps(result)}						
	return direct_to_template(request, "raw.html", context)							
	
def tweetdata(request):
	result = {}
	data = request.POST
	if data.has_key("id_str"):
		result["org_content"] = "no content available"
		result["profile_image_url"] = "http://a3.twimg.com/sticky/default_profile_images/default_profile_2_normal.png"
		d = getCollDrops().find_one({"id_str":data["id_str"]})
		if not d:
			d = getCollDrops().find_one({"retweet_id_str":data["id_str"]})
		if d:
			d = timediffDrop(d, parse(str(d["created_at"])), "timediff")			
			result["name"] = d["name"]
			result["timediff"] = d["timediff"]
			result["screen_name"] = d["screen_name"]
			result["org_content"] = striptags(d["org_content"])
			result["profile_image_url"] = d["user"]["profile_image_url"]
	context = {"json": simplejson.dumps(result)}
	return direct_to_template(request, "raw.html", context)
		
def handleOpenClose(request, closing):
	l_id_str = []
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:		
			data = request.POST
			drop_id = data["_id"]
			drop = getCollDrops().find_one({"_id": objectid.ObjectId(drop_id)})	
			if not drop:
				clog("mailDrop: can't find drop")
			else:
				user_id_str = drop["user_id_str"]
				drops = getCollDrops().find({"user_id_str": user_id_str}, fields=["id_str"], sort=[("added_at_precise", -1)]).limit(30)
				for id_str in drops:
					l_id_str.append(id_str["id_str"])
				if "closed_drops" not in user:
					user["closed_drops"] = []
				if closing:
					user["closed_drops"].append(user_id_str)
					user["closed_drops"] = list(set(user["closed_drops"]))
				else:
					if user_id_str in user["closed_drops"]:
						user["closed_drops"].remove(user_id_str)
				getCollUsers().save(user, safe=True)
	return l_id_str
				
def openitem(request):
	clog("opening a drop")
	result = {}
	result["peers"] = handleOpenClose(request, False)		
	context = {"json": simplejson.dumps(result)}
	return direct_to_template(request, "raw.html", context)				

def closeitem(request):
	clog("closing a drop")
	result = {}
	result["peers"] = handleOpenClose(request, True)		
	context = {"json": simplejson.dumps(result)}
	return direct_to_template(request, "raw.html", context)				
	
def timediffDrop(drop, comparetime, diffname):
	ddrop =  comparetime
	dnow = datetime.datetime.utcnow()
	timediff = dnow - ddrop
	if timediff.days>0:
		if timediff.days==1:
			drop[diffname]=str(timediff.days)+" day ago"
		else:
			drop[diffname]=str(timediff.days)+" days ago"
	elif timediff.seconds<(24*60*60) and timediff.seconds>60*60:
		if timediff.seconds>60*60 and timediff.seconds<2*60*60:
			drop[diffname]="1 hour ago"
		else:
			drop[diffname]=str(timediff.seconds/60/60)+" hours ago"
	elif timediff.seconds<60*60:
		if timediff.seconds<60:
			drop[diffname]="less then 1 minute ago"
		elif timediff.seconds>60 and timediff.seconds<60*2:
			drop[diffname]="1 minute ago"
		else:
			drop[diffname]=str(timediff.seconds/60)+" minutes ago"
	return drop

def processDropForUI(drop, retweeted_ids, user):	
	drop = timediffDrop(drop, parse(str(drop["created_at"])), "timediff")			
	if drop["retweeted"]:
		drop = timediffDrop(drop, parse(str(drop["retweet_created_at"])), "retweet_timediff")
	del drop["created_at"]
	if "retweet_created_at" in drop:
		del drop["retweet_created_at"]
	del drop["added_at"]
	if "followed_links" in drop.keys():
		for fl in  drop["followed_links"]: 
			if "link" in fl:
				if "etag" in fl["link"]:
					del fl["link"]["etag"]		
	drop["_id"] = str(drop["_id"])
	drop["isfavorite"] = False
	drop["isnotfavorite"] = True
	if "favorites" in drop:
		user_id_str = int(user["id_str"])
		if user_id_str in drop["favorites"]:
			drop["isfavorite"] = True
			drop["isnotfavorite"] = False
	drop["isretweeted"] = False
	drop["isnotretweeted"] = True
	if "retweet_id_str" in drop:
		if int(drop["id_str"]) in retweeted_ids or int(drop["retweet_id_str"]) in retweeted_ids:
			drop["isretweeted"] = True
			drop["isnotretweeted"] = False
	else:
		if int(drop["id_str"]) in retweeted_ids:
			drop["isretweeted"] = True
			drop["isnotretweeted"] = False
	drop["closed_by_system"] = True
	if "protected" in drop["user"]:
		if drop["user"]["protected"]==True:
			if drop["user"]["id"] not in user["twitter_friend_list"]:
				drop["org_content"] = "this tweet is protected by the user and only visible for approved followers."
				if "followed_links" in drop:
					drop["followed_links"] = []
	return drop

def getIdsList(user, slug):
	if "lists" in user:
		for l in user["lists"]:
			if l["slug"]==slug:
				return l["members"]
	return []
	
def listToMongoOr(l, keyword):
	# converts a list to an orred mongoquery
	#{ $or : [ { 'keyword' : 1 } , { 'keyword' : 2 } ] } )
	s = "["
	c = 0
	for i in l:
		s += "{'"+keyword+"':'"+i+"'}"
		if c<len(l)-1:
			s += ","
		c += 1
	s += "]"
	return s

def getDropsForUser(user, timestamp_page_refresh, page, screen_name, pagelen, last_added_at_precise, ulist):
	coll = getCollDrops()
	drops = []
	last_added_at_precise = float(last_added_at_precise)	
	if last_added_at_precise!=0:				
		timestamp_page_refresh = last_added_at_precise
	timestamp_page_refresh = float(timestamp_page_refresh)
	dcoll = None
	if screen_name and screen_name!="None":		
		if screen_name=="list":
			dcoll = coll.find({"list_slugs":ulist, "newsrivr_userid_md5":user["newsrivr_userid_md5"], "added_at_precise":{"$lt": timestamp_page_refresh} }, sort=[("added_at_precise", -1)])
		elif screen_name=="mentions":
			dcoll = coll.find({"mentions":"@"+user["screen_name"],  "added_at_precise":{"$lt": timestamp_page_refresh}}, sort=[("added_at_precise", -1)])
		elif screen_name=="favorites":
			dcoll = coll.find({"favorites":int(user["id_str"]),  "added_at_precise":{"$lt": timestamp_page_refresh}}, sort=[("added_at_precise", -1)])
		else:
			dcoll = coll.find({"screen_name":screen_name,  "added_at_precise":{"$lt": timestamp_page_refresh}}, sort=[("added_at_precise", -1)])
	else:
		if "screen_name" in user:
			dcoll = coll.find({"newsrivr_userid_md5":user["newsrivr_userid_md5"], "added_at_precise":{"$lt": timestamp_page_refresh} }, sort=[("added_at_precise", -1)])
			
	if "screen_name" in user:
		retweeted_ids = []
		for retweet_id in getCollDrops().find({"screen_name":user["screen_name"], "retweeted":True}):
			retweeted_ids.append(int(retweet_id["retweet_id_str"]))
	if not dcoll:
		return [], 0, 0

	for drop in dcoll.limit(pagelen+1):
		drop = processDropForUI(drop, retweeted_ids, user)
		drops.append(drop)
	total_for_user = 1000000
	if len(drops)<pagelen:
		total_for_user = len(drops)
	
	if len(drops)>1:
		last_added_at_precise = "%.9f" % drops[len(drops)-2]["added_at_precise"]
	elif len(drops)>0:
		last_added_at_precise = "%.9f" % drops[len(drops)-1]["added_at_precise"]			
	else:
		last_added_at_precise = 0

	for d in drops:
		d["cannot_be_opened"] = d["can_be_opened"]== False
		d["post_open"] = True			
		d["post_closed"] = False
		if "closed_drops" in user:
			if d["user_id_str"] in user["closed_drops"]:
				d["post_closed"] = True
				d["post_open"] = False
	return drops, total_for_user, last_added_at_precise

def get_json_drops(request, page, template, screen_name, last_added_at_precise, resetCookie=False, ulists=None, ulist=None):
	pagelen = 10
	response = HttpResponseRedirect("/signin/")
	title = "NewsRivr"
	if screen_name and screen_name!="None":
		title += " | "+capfirst(screen_name)
		if screen_name=="list":
			title += ": "+capfirst(ulist)
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		timestamp_page_refresh = None
		if not request.COOKIES.has_key("timestamp_page_refresh") or resetCookie:
			dt, dtms = getTimeWithMS()			
			timestamp_page_refresh = str(dtms)
		else:
			timestamp_page_refresh = str(request.COOKIES["timestamp_page_refresh"])			
		userid = request.COOKIES["newsrivr_userid_md5"]
		if userid!="None":
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
			if not user or "access_token" not in user:
				return response
			user["id"]=str(user["_id"])
			if user:
				ios = False
				ie8 = False
				tablet = False
				if request.META.has_key('HTTP_USER_AGENT'):
					meta = request.META["HTTP_USER_AGENT"].lower()
					ios = ismobile(request)
					if "msie" in meta.lower():
						ie8 = True
					if "msie 9.0" in meta.lower():
						ie8 = False
					if "ipad" in meta.lower():
						tablet = True

				#ios = tablet = True
				# tablet = False
				
				if ios:
					pagelen = 10
				context = {}
				if template:
					drops, total_for_user, last_added_at_precise = getDropsForUser(user, timestamp_page_refresh, page, screen_name, pagelen, last_added_at_precise, ulist)					
					if ie8:
						for d in drops:
							for l in d["followed_links"]:
								if "image" in l:
									if "base64" in l["image"]["src"]:
										idata = cStringIO.StringIO(base64.decodestring(l["image"]["src"].replace("data:jpeg/png;base64,", "")))
										i = Image.open(idata)
										nh = float(i.size[1]) / float(i.size[0]) * int(float(i.size[0])/2)
										nw = int(float(i.size[0])/2)
										i = i.resize((int(float(i.size[0])/2), int(nh)))
										outdata = cStringIO.StringIO()
										i.save(outdata, "jpeg")
										l["image"]["src"] = "data:image/jpeg;base64,"+base64.encodestring(outdata.getvalue())
										l["image"]["width"] = nw
					for d in drops:
						if "profile_image_url_big_base64" in d:
							d["profile_image_url"] = d["profile_image_url_small_base64"]						
					paginator = Paginator(drops, pagelen)
					page_obj = paginator.page(1)
					tiledbackground = True
					twitter_credentials = None
					has_next = False
					if page_obj.has_next():
						has_next = True
					nodrops = False
					if len(drops)==0:
						nodrops==True
					context = {				
						"json": simplejson.dumps({"drops":page_obj.object_list,
												  "nodrops":nodrops,
												  "first_run":False,
												  "last_added_at_precise":last_added_at_precise,
												  "has_next": has_next,
												  "total_for_user":total_for_user}),   
					};
				else:
					if ios:
						drops, total_for_user, last_added_at_precise = getDropsForUser(user, timestamp_page_refresh, page, screen_name, pagelen, last_added_at_precise, ulist)
						if ios:
							for d in drops:
								if tablet:
									if "profile_image_url_big_base64" in d:
										d["profile_image_url_big"] = d["profile_image_url_big_base64"]
									else:
										d["profile_image_url_big"] = d["user"]["profile_image_url"].replace("_normal", "_reasonably_small")										
									if "retweeted" in d:
										if d["retweeted"]:
											d["retweet_profile_image_url_big"] = d["retweet_profile_image_url"].replace("_normal", "_reasonably_small")
								else:
									if "profile_image_url_big_base64" in d:
										d["profile_image_url_big"] = d["profile_image_url_small_base64"]
									else:										
										d["profile_image_url_big"] = d["user"]["profile_image_url"]
									if "retweeted" in d:
										if d["retweeted"]:
											d["retweet_profile_image_url_big"] = d["retweet_profile_image_url"]
									
								for l in d["followed_links"]:
									if tablet:
										if "image" in l:
											if "thumbnail" in l["image"]:
												d["profile_image_url_big"] = l["image"]["thumbnail"]																					
											else:
												d["profile_image_url_big"] = l["image"]["src"]
									html = ""													
									if "simplehtml" in l:			
										soup = BeautifulSoup(l["simplehtml"])
										for tag in soup.findAll(True):
											if tag.has_key("id"):
												if "nr_hide_" in str(tag["id"]):
													tag.hidden = True
												if "nr_readmore_" in str(tag["id"]):
													tag.extract()
										l["simplehtml"] = soup.renderContents()
					else:
						drops = None
						total_for_user = 0
						context = {
							"first_run":True,
							"ulist":None
						};						
					if "twitter_credentials" in user:
						profile_image_url = None
						profile_image_url_big = None
						profile_name = None
						profile_url = None
						profile_description = None
						profile_location = None							
						twitter_credentials = user["twitter_credentials"]
						if "profile_background_tile" in user["twitter_credentials"]:
							tiledbackground = user["twitter_credentials"]["profile_background_tile"]
							profile_use_background_image = twitter_credentials["profile_use_background_image"]
							profile_background_color = twitter_credentials["profile_background_color"]
							profile_background_image_url = twitter_credentials["profile_background_image_url"]
						if screen_name:
							other_user_drop = getCollDrops().find_one({"screen_name":screen_name})
							if other_user_drop:
								other_user = other_user_drop["user"]
								if other_user:
									#other_twitter_credentials = other_user["twitter_credentials"]
									tiledbackground = other_user["profile_background_tile"]
									profile_use_background_image = other_user["profile_use_background_image"]
									profile_background_color = other_user["profile_background_color"]
									profile_background_image_url = other_user["profile_background_image_url"]
									profile_image_url = other_user["profile_image_url"]
									profile_image_url_big = other_user["profile_image_url"].replace("_normal", "_reasonably_small")
									profile_name = other_user["name"]
									if not profile_name:
										profile_name = "";
									profile_url = other_user["url"]
									if not profile_url:
										profile_url = "";										
									profile_description = other_user["description"]
									if not profile_description:
										profile_description = "";																				
									profile_location = other_user["location"]
									if not profile_location:
										profile_location = "";																										
						sd = None
						if "share_data" in user:
							sd = user["share_data"]
							if "previous_emails" in sd:
								sd["previous_emails"].sort()
						cangoback = False
						if int(page)>1:
							cangoback = True							
						dropslice = None
						if drops:
							dropslice=drops[0:pagelen]
						hasnextpage = False
						if total_for_user > (int(page)*int(pagelen)):
							hasnextpage = True							
						ulist_full_name = None
						if ulist:
							if "lists" in user:
								for l in user["lists"]:
									if l["slug"]==ulist:
										ulist_full_name = l["name"]
						nodrops = False
						if screen_name=="lists":
							nodrops = True
						context = {
							"first_run":False,
							"tuser":twitter_credentials,
							"tuser_profile_use_background_image":profile_use_background_image,
							"tuser_profile_background_color":profile_background_color,
							"tuser_profile_background_image_url":profile_background_image_url,
							"profile_image_url":profile_image_url,
							"profile_image_url_big":profile_image_url_big,
							"profile_name":profile_name,
							"profile_url":profile_url,
							"profile_description":profile_description,
							"profile_location":profile_location,
							"first_added_at_precise":0,
							"last_added_at_precise":last_added_at_precise,
							"ios":ios,
							"ie8":ie8,
							"randomnumber":random.randint(1000, 1000000),
							"tablet":tablet,
							"range100":range(0,100),
							"tiledbackground":tiledbackground,
							"user":user,
							"screen_name":screen_name,
							"current_page":page,
							"sd":sd,
							"title":title,
							"drops":dropslice,
							"nextpage":int(page)+1,
							"prevpage":int(page)-1,
							"cangoback":cangoback,
							"total_for_user":total_for_user,
							"hasnextpage":hasnextpage,
							"ulists":ulists,
							"ulist":ulist,
							"nodrops":nodrops,
							"ulist_full_name":ulist_full_name
						};
				if not template:
					if ios:
						template = "jqm_index.html"
					else:
						template = "index.html"
						#template = "indexmobile.html"
				return direct_to_template(request, template, context)	
	return response
		
def indexmain(request, page, screen_name, resetCookie=False, ulists=None, ulist=None, last_added_at_precise=0):
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
		if user:
			dt, dtms = getTimeWithMS()			
			user["last_login"] = str(dtms)
			if "login_count" in user:
				if type(user["login_count"])==type([]):
					user["login_count"] = len(user["login_count"])
				else:
					user["login_count"] = user["login_count"] + 1
			else:
				user["login_count"] = 1
			if request.META.has_key('HTTP_USER_AGENT'):				
				if "agent" not in user:
					user["agent"] = []
				user["agent"].append(toUTF8(str(request.META["HTTP_USER_AGENT"]).lower()))
				user["agent"] = list(set(user["agent"]))
			getCollUsers().save(user, safe=True)
	if resetCookie:
		dt, dtms = getTimeWithMS()
		cookietime = str(dtms)
	else:
		if request.COOKIES.has_key("timestamp_page_refresh"):
			timestamp_page_refresh = str(request.COOKIES["timestamp_page_refresh"])
			cookietime = float(timestamp_page_refresh)
	if last_added_at_precise!=0:
		cookietime = last_added_at_precise
	response = get_json_drops(request, page, None, screen_name, cookietime, ulists=ulists, ulist=ulist)
	if resetCookie:
		setCookie(response, "timestamp_page_refresh", cookietime)	
	return response
		
def jqmactions(request, id_str):
	context = {}
	context["id_str"] = id_str;	
	return direct_to_template(request, "jqm_actions.html", context)
		
def addDropToContext(request, user, context, id_str):
	context["hastext"] = False
	context["randomnumber"] = random.randint(1000, 1000000)
	if not user:
		if request.COOKIES.has_key("newsrivr_userid_md5"):
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])			
	if user:
		ios = False
		ie8 = False
		tablet = False				
		if request.META.has_key('HTTP_USER_AGENT'):
			meta = request.META["HTTP_USER_AGENT"].lower()
			ios = ismobile(request)
			if "msie" in meta.lower():
				ie8 = True
			if "msie 9.0" in meta.lower():
				ie8 = False
			if "ipad" in meta.lower():
				tablet = True
		if osname:
			if "Darwin" in osname:							
				ios = tablet = True
				pass
		#tablet = False
		d = getCollDrops().find_one({"id_str":id_str})
		if d:
			d["objid"] = d["_id"]
			d["hascontent"] = False
			if "screen_name" in user:
				retweeted_ids = []
				for retweet_id in getCollDrops().find({"screen_name":user["screen_name"], "retweeted":True}):
					retweeted_ids.append(int(retweet_id["retweet_id_str"]))
			d = processDropForUI(d, retweeted_ids, user)
			d["profile_image_url_big"] = d["user"]["profile_image_url"].replace("_normal", "_reasonably_small")
			if "images" in d:
				if len(d["images"])>0:
					d["hascontent"] = True			
			for l in d["followed_links"]:
				if "image" in l:
					d["hascontent"] = True
				if tablet:
					if "image" in l:
						if l["image"]["width"]>640:
							l["image"]["width"]=640
				else:
					if "image" in l:
						if l["image"]["width"]>240:
							l["image"]["width"]=240
				html = ""													
				if "simplehtml" in l:			
					soup = BeautifulSoup(l["simplehtml"])
					for tag in soup.findAll(True):
						if tag.has_key("id"):
							if "nr_hide_" in str(tag["id"]):
								tag.hidden = True
							if "nr_readmore_" in str(tag["id"]):
								tag.extract()
					l["simplehtml"] = soup.renderContents()
					if len(l["simplehtml"])>0 and not context["hastext"]:
						context["hastext"] = True
						d["hascontent"] = True
		context["drop"] = d
	if "drop" not in context:
		clog("addDropToContext: warning could not find drop to add to context")
	return context

def jqm_reply_dialog(request, id_str):
	context = {}	
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
	if user:	
		context = addDropToContext(request, user, context, id_str)
	return direct_to_template(request, "jqm_reply.html", context)
	
def jqm_share_dialog(request, id_str):
	context = {}	
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
	if user:	
		sd = None
		if "share_data" in user:
			sd = user["share_data"]
			if "previous_emails" in sd:
				sd["previous_emails"].sort()
		context["sd"] = sd
		context = addDropToContext(request, user, context, id_str)
	return direct_to_template(request, "jqm_sharedialog.html", context)
	
def jqmtweet(request, id_str):
	context = {}		
	context = addDropToContext(request, None, context, id_str)
	return direct_to_template(request, "jqm_tweet.html", context)
	
def pageindex(request, page, screen_name=None, last_added_at_precise=0, list_name=None, randnr=0):
	return indexmain(request, page, screen_name, resetCookie=(int(page)==1), last_added_at_precise=last_added_at_precise, ulist=list_name);

def index_lists(request):
	user = None
	if request.COOKIES.has_key("newsrivr_userid_md5"):
		user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
	ulist = []
	if user:
		d = {}
		if "lists" in user:
			for i in user["lists"]:
				d[i["name"]] = i
			ks = d.keys()
			ks.sort()
			for i in ks:
				ulist.append(d[i])
	response = indexmain(request, 1, screen_name="lists", resetCookie=True, ulists=ulist);
	return response

def index_list(request, list_name):
	response = indexmain(request, 1, "list", resetCookie=True, ulist=list_name);
	return response
	
def index(request, screen_name=None, randnr=0):
	response = indexmain(request, 1, screen_name, resetCookie=True);
	return response

def index_mentions(request):
	return index(request, screen_name="mentions")

def index_favorites(request):	
	return index(request, screen_name="favorites")

def index_user(request, screen_name):
	return index(request, screen_name)
	
def index_json(request, page, screen_name, last_added_at_precise, list_name):
	return get_json_drops(request, page, "raw.html", screen_name, last_added_at_precise, ulist=list_name)

def testdata(request):
	d = {}
	for i in range(0, 200):
		d[i] = "hello world"
	context = {"json": simplejson.dumps(d)}
	return direct_to_template(request, "raw.html", context)
	
def new_drops_count_json(request, screen_name, list_name):
	try:
		cnt = 0
		context = {}
		pagelen = 10
		if request.COOKIES.has_key("newsrivr_userid_md5"):
			user = getUserByMD5(request.COOKIES["newsrivr_userid_md5"])
			if user and "access_token" in user:
				timestamp_page_refresh = None
				if not request.COOKIES.has_key("timestamp_page_refresh"):
					dt, dtms = getTimeWithMS()			
					timestamp_page_refresh = str(dtms)
				else:
					timestamp_page_refresh = str(request.COOKIES["timestamp_page_refresh"])
				timestamp_page_refresh = float(timestamp_page_refresh)
				coll = getCollDrops()
				
				if screen_name and screen_name!="None":
					if screen_name=="list":
						lst = getIdsList(user, list_name)
						orquery = listToMongoOr(lst, "created_by")
						if len(lst)==0:
							cnt = 0
						else:
							cnt = coll.find({"$or":eval(orquery), "newsrivr_userid_md5":user["newsrivr_userid_md5"], "added_at_precise":{"$gt": timestamp_page_refresh} }).count()
					elif screen_name=="mentions":
						cnt = coll.find({"mentions":"@"+user["screen_name"],  "added_at_precise":{"$gt": timestamp_page_refresh}}).count()
					elif screen_name=="favorites":
						cnt = coll.find({"favorites":int(user["id_str"]),  "added_at_precise":{"$gt": timestamp_page_refresh}}).count()
					else:
						cnt = coll.find({"screen_name":screen_name,  "added_at_precise":{"$gt": timestamp_page_refresh}}).count()
				else:
					if "screen_name" in user:
						cnt = coll.find({"newsrivr_userid_md5":user["newsrivr_userid_md5"], "added_at_precise":{"$gt": timestamp_page_refresh} }).count()
				if cnt>0:
					dt, dtms = getTimeWithMS()
					drops, total_for_user, last_added_at_precise = getDropsForUser(user, dtms, 1, screen_name, pagelen, 0, list_name)
					for d in drops:
						if "profile_image_url_big_base64" in d:
							d["profile_image_url"] = d["profile_image_url_small_base64"]
					paginator = Paginator(drops, pagelen)
					page_obj = paginator.page(1)
					has_next = False
					if page_obj.has_next:
						has_next = True
					context = {"json": simplejson.dumps({"drops":page_obj.object_list, "last_added_at_precise":last_added_at_precise, "cnt":cnt, "has_next": has_next, "total_for_user":total_for_user})}
				else:				
					context = {"json": simplejson.dumps({"drops":[], "cnt":cnt})}	
		return direct_to_template(request, "raw.html", context)
	except Exception, e:
		import traceback
		import StringIO
		s = StringIO.StringIO()
		traceback.print_exc(file=s)
		clog(s.getvalue())
		
def resetcookietimestamp(request):
	context = {"json": 1}
	response = direct_to_template(request, "raw.html", context)
	dt, dtms = getTimeWithMS()
	setCookie(response, "timestamp_page_refresh", str(dtms))
	return response
	
def signin(request):
	response = render_to_response("content_signin.html")
	user = getCurrentUser(request);	
	setCookie(response, "newsrivr_userid_md5", str(user["newsrivr_userid_md5"]))		
	return response
	
def signout(request):
	response = render_to_response("content_signout.html")
	response.delete_cookie("newsrivr_userid_md5"); 
	return response

def optout(request):
	response = render_to_response("content_optout.html")
	user = getCurrentUser(request)	
	coll = getCollDrops()
	drops = []
	for drop in coll.find({"newsrivr_userid_md5":user["newsrivr_userid_md5"]}):
		coll.remove({"_id":ObjectId(drop["_id"])})		
	getCollUsers().remove({"_id":ObjectId(user["_id"])})
	clog("delete cookie optout")
	response.delete_cookie("newsrivr_userid_md5");
	return response

def unauth(request):
	response = HttpResponseRedirect(reverse("twitter_oauth_main"))
	request.session.clear()
	return response

def auth(request):
	"/auth/"
	CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
	CONNECTION = httplib.HTTPSConnection(SERVER)	
	token = get_unauthorised_request_token(CONSUMER, CONNECTION)
	auth_url = get_authorisation_url(CONSUMER, token)
	response = HttpResponseRedirect(auth_url)
	user = getCurrentUser(request);
	user["unauthed_token"] = token.to_string()
	users = getCollUsers()	
	users.save(user, safe=True)	
	return response
					
def return_(request):
	"/return/"
	CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
	CONNECTION = httplib.HTTPSConnection(SERVER)		
	unauthed_token = user = getCurrentUser(request)["unauthed_token"]
	if not unauthed_token:
		return HttpResponse("No un-authed token cookie")
	token = oauth.OAuthToken.from_string(unauthed_token)
	if token.key != request.GET.get("oauth_token", "no-token"):
		return HttpResponse("Something went wrong! Tokens do not match")
	access_token = exchange_request_token_for_access_token(CONSUMER, CONNECTION, token)	
	clog(str(access_token))
	exis_user = getCollUsers().find_one({"access_token":str(access_token)})
	response = HttpResponseRedirect("/")
	user = getCurrentUser(request);
	if exis_user and user["_id"]!=exis_user["_id"]:
		users = getCollUsers()
		clog("delete temp user")
		users.remove({"_id":user["_id"]}, safe=True)
		setCookie(response, "newsrivr_userid_md5", str(exis_user["newsrivr_userid_md5"]))		
	else:
		user["access_token"] = access_token.to_string()
		user["newuser"] = True
		users = getCollUsers()	
		users.save(user, safe=True)
	return response
