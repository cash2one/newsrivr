from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import dict
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
#!/usr/bin/env python
import os
import pymongo
import locale
import time
import urllib.parse
from datetime import datetime
from oauthtwitter import OAuthApi
from dateutil.parser import parse

if "Darwin" in os.popen("uname").read():
	MONGOSERVER = 'localhost'
else:
	MONGOSERVER = '192.168.167.192'
MONGOPORT = 27017

consumer_key = "sRXKCWePy0kG43DwiG9kw"
consumer_secret = "ikO6z1CVFW4tv4NmpNo8QbhCHMQNjOq1Z7vWc25wA"

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

def insertTweet(id, user, tweet):
    col = getCollUnprocessedTweets()
    curs = col.find({"id_str":id})
    if curs.count()>0:
        for t in curs:            
            if not user in t["newsrivr_userid_md5"]:
                t["newsrivr_userid_md5"].append(user)
                col.save(t)
    else:
        col.insert(tweet)
    return False

def parseDatetime(string):
    return parse(string)

def main():
    for user in getCollUsers().find():
        if "access_token" in user and "twitter_credentials" in user:
            #if user["screen_name"]=="rabshakeh":
            print(user["screen_name"])
            access_token = dict(urllib.parse.parse_qsl(user["access_token"]))
            twitter = OAuthApi(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
            #user["twitter_credentials"] = twitter.VerifyCredentials()
            user_timeline = twitter.GetHomeTimeline({"count":5})                
            ut = getCollUnprocessedTweets()
            for tweet in user_timeline:
            	tweet["inprocess"]=0
            	tweet["for_user"]=int(user["id_str"])
            	tweet["created_at_utc"]=str(tweet["created_at"])
            	tweet["created_at"]=parseDatetime(tweet["created_at"])
            	tweet["newsrivr_userid_md5"]=[user["newsrivr_userid_md5"]]
            	insertTweet(tweet["id_str"], user["newsrivr_userid_md5"], tweet)
            friends = twitter.GetFriendsIDs()
            friend_list = []
            for fp in friends:                
            	friend_list.append(fp)
            user["twitter_friend_list"]=friend_list
            getCollUsers().save(user)
        
if __name__=="__main__":
    main()
    print("done")
