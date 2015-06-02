from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import dict
from future import standard_library
standard_library.install_aliases()
from builtins import str
#!/usr/bin/env python
from d_utils import *
	
def clog(s):
    s= str(s)
    print('\033[%94m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m')
    
def deleteDrops(dropids):
    for did in dropids:
        getCollDrops().remove({"id_str":did}, safe=True)
        getCollYoutubeTags().remove({"id_str":did}, safe=True)
        getCollImageMd5s().remove({"id_str":did}, safe=True)
        getCollProcessedTweets().remove({"id_str":did}, safe=True)

def main():
	try:
		while True:
			crs = getCollUsers().find({"newuser":True})
			if crs.count()>0:
				clog("checking for newusers: "+str(crs.count())+" found")
			for u in crs:
				u["newuser"]=False
				u["userneedstweets"]=True            
				access_token = dict(urlparse.parse_qsl(u["access_token"]))
				twitter = OAuthApi(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
				u["twitter_credentials"] = twitter.VerifyCredentials()
				u["id_str"] = u["twitter_credentials"]["id_str"]
				u["screen_name"] = u["twitter_credentials"]["screen_name"]
				getCollUsers().save(u, safe=True)
				
				users_same_name = []
				# find out if there are more users with the same screenname, this can happen after an deny.
				crs = getCollUsers().find({"screen_name":u["screen_name"]}, sort=[("date_created", 1)])
				for i in crs:
					users_same_name.append(i)
					
				old_newsrivr_userid_md5 = None
				new_newsrivr_userid_md5 = None
				if len(users_same_name)>1:
					old_newsrivr_userid_md5 = users_same_name[0]["newsrivr_userid_md5"]
					new_newsrivr_userid_md5 = users_same_name[len(users_same_name)-1]["newsrivr_userid_md5"]
					if "closed_drops" in users_same_name[0]:
						users_same_name[len(users_same_name)-1]["closed_drops"] = users_same_name[0]["closed_drops"]
					if "share_data" in users_same_name[0]:
						users_same_name[len(users_same_name)-1]["share_data"] = users_same_name[0]["share_data"]
					getCollUsers().save(users_same_name[len(users_same_name)-1], safe=True)
					
				if old_newsrivr_userid_md5 and new_newsrivr_userid_md5:
					cnt = 0
					for d in getCollDrops().find({"newsrivr_userid_md5":old_newsrivr_userid_md5}):
						d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))
						d["newsrivr_userid_md5"].remove(old_newsrivr_userid_md5)
						d["newsrivr_userid_md5"].append(new_newsrivr_userid_md5)
						for i in getCollDrops().find({"id_str":d["id_str"]}):
							if i["_id"]!=d["_id"]:
								d["newsrivr_userid_md5"].extend(i["newsrivr_userid_md5"])
								d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))        
								getCollDrops().remove({"_id":pymongo.objectid.ObjectId(i["_id"])}, safe=True)
											
						getCollDrops().save(d, safe=True)
						cnt += 1
						if cnt%100==0:
							clog("user changed md5, correcting: "+ str(cnt))
					for u in users_same_name:
						if u["newsrivr_userid_md5"]!=new_newsrivr_userid_md5:
							getCollUsers().remove({"_id":pymongo.objectid.ObjectId(u["_id"])}, safe=True)
							drops_to_remove = []
							for d in getCollDrops().find({"newsrivr_userid_md5":u["newsrivr_userid_md5"]}):
								d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))
								d["newsrivr_userid_md5"].remove(u["newsrivr_userid_md5"])
								if len(d["newsrivr_userid_md5"])==0: 
									drops_to_remove.append(d["id_str"])
								else:
									getCollDrops().save(d, safe=True)
							deleteDrops(drops_to_remove)
				clog("done")
			time.sleep(1)
	except (Exception) as e:
		mailException(e)
		        
if __name__=="__main__":
	clog("newuser daemon online")
	driver(main, inspect.getfile(inspect.currentframe()))

