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
from d_utils import *

def clog(s):
    s= str(s)
    print('\033[%91m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m')

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
	try:
		while True:
			crs = getCollUsers().find({"userneedstweets":True})
			if crs.count()>0:
				clog("checking for initial tweet requiring users: "+str(crs.count())+" found")        
			for user in crs:
				clog(user["twitter_credentials"]["name"])
				if "access_token" in user:
					access_token = dict(urlparse.parse_qsl(user["access_token"]))
					twitter = OAuthApi(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])        
					user_timeline = twitter.GetHomeTimeline({"count":30})
					ut = getCollUnprocessedTweets()
					for tweet in user_timeline:
						tweet["inprocess"]=0
						tweet["created_at"]=parseDatetime(tweet["created_at"])
						tweet["newsrivr_userid_md5"]=[user["newsrivr_userid_md5"]]
						tweet["for_user"] = int(user["id_str"])
						insertTweet(tweet["id_str"], user["newsrivr_userid_md5"], tweet)					
					friends = twitter.GetFriendsIDs()                
					friend_list = []
					for fp in friends:                
						friend_list.append(fp)
					user["twitter_friend_list"]=friend_list
					user["twitter_credentials"] = twitter.VerifyCredentials()
					user["userneedstweets"] = False
					getCollUsers().save(user)
					dlist = {}
					dlist["for_user"] = int(user["id_str"])
					dlist["event"] = None
					dtn, dtnms = getTimeWithMS()
					dlist["added_at"] = dtn
					dlist["added_at_precise"] = dtnms						
					if getCollLists().find({"for_user":dlist["for_user"], "event":None}).count()==0:
						getCollLists().save(dlist, safe=True)					
			time.sleep(1)                
	except (Exception) as e:
		mailException(e)

if __name__=="__main__":
    clog("new user tweet deamon online")
    driver(main, inspect.getfile(inspect.currentframe()))
