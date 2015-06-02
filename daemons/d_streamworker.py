#!/usr/bin/env python
from d_utils import *

def clog(s):
	s= str(s)
	print '\033[%92m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m'
	
def getUserByIDStr(id_str):
	users = getCollUsers()
	sd = {"id_str": str(id_str)}
	return users.find_one(sd)
	
def updateFriends(user, friends):
	u = getUserByIDStr(user)
	if u:
		u["twitter_friend_list"] = friends
		getCollUsers().save(u, safe=True)

def updateProfile(user, profile):
	clog("new profile")
	u = getUserByIDStr(user)
	if u:
		u["twitter_credentials"] = profile
		getCollUsers().save(u, safe=True)
		for d in getCollDrops().find({"user_id_str":u["id_str"]}):
			d["user"] = profile
			d["profile_image_url"] = d["user"]["profile_image_url"]
			#clog("updating:"+d["org_content"])
			getCollDrops().save(d, safe=True)

def deleteDrops(dropids):
	for did in dropids:
		getCollDrops().remove({"id_str":did}, safe=True)
		getCollYoutubeTags().remove({"id_str":did}, safe=True)
		getCollImageMd5s().remove({"id_str":did}, safe=True)
		getCollProcessedTweets().remove({"id_str":did}, safe=True)
		
def insertTweet(id, user, tweet):
	col = getCollUnprocessedTweets()
	t = col.find_one({"id_str":id})
	if t:
		if not user in t["newsrivr_userid_md5"]:
			t["newsrivr_userid_md5"].append(user)
			col.save(t)
	else:
		col.insert(tweet)
	return False

def getUserByMD5(md5):
	users = getCollUsers()
	sd = {"newsrivr_userid_md5": md5}
	return users.find_one(sd)
	
class fetchTimeLine(multiprocessing.Process):
	def __init__(self, newsrivr_userid_md5):
		multiprocessing.Process.__init__(self)
		self.newsrivr_userid_md5 = newsrivr_userid_md5
	def run(self):
		time.sleep(30)
		user = getUserByMD5(self.newsrivr_userid_md5)
		access_token = dict(urlparse.parse_qsl(user["access_token"]))
		twitter = OAuthApi(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])		
		user_timeline = twitter.GetHomeTimeline({"count":10})
		ut = getCollUnprocessedTweets()
		for tweet in user_timeline:
			tweet["inprocess"]=0
			tweet["for_user"]=int(user["id_str"])
			tweet["created_at_utc"]=str(tweet["created_at"])
			tweet["created_at"]=parse(tweet["created_at"])
			tweet["newsrivr_userid_md5"]=[user["newsrivr_userid_md5"]]
			insertTweet(tweet["id_str"], user["newsrivr_userid_md5"], tweet)
		friends = twitter.GetFriendsIDs()
		friend_list = []
		for fp in friends:				
			friend_list.append(fp)
		user["twitter_friend_list"]=friend_list
		getCollUsers().save(user)
		
def deleteDropsForUser(user, oldfriendid):
	user = getUserByIDStr(user)
	if user:
		drops_to_remove = []
		for d in getCollDrops().find({"newsrivr_userid_md5":user["newsrivr_userid_md5"]}):
			if int(d["user_id_str"])==int(oldfriendid):
				d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))
				d["newsrivr_userid_md5"].remove(user["newsrivr_userid_md5"])
				if len(d["newsrivr_userid_md5"])==0: 
					drops_to_remove.append(d["id_str"])
				else:
					getCollDrops().save(d, safe=True)
		clog("delete "+str(len(drops_to_remove))+" drops "+str(oldfriendid)+" for user "+str(user["screen_name"]))
		deleteDrops(drops_to_remove)

def subscribe(follow_messages_received):
	for user in follow_messages_received:
		nruser = getUserByIDStr(user)		
		for target in follow_messages_received[user]:
			if nruser:
				clog("fetching timeline for user:"+nruser["screen_name"])
				tnf = fetchTimeLine(nruser["newsrivr_userid_md5"])
				tnf.start()

def unsubscribe(unfollow_messages_received):
	drops_to_remove = []	
	for user in unfollow_messages_received:
		nruser = getUserByIDStr(user)		
		for target in unfollow_messages_received[user]:
			if nruser:			
				clog("removing drops")
				for d in getCollDrops().find({"user_id_str":target}):
					if nruser["newsrivr_userid_md5"] in d["newsrivr_userid_md5"]:
						d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))
						d["newsrivr_userid_md5"].remove(nruser["newsrivr_userid_md5"])
						if len(d["newsrivr_userid_md5"])==0: 
							drops_to_remove.append(d["id_str"])
						else:
							getCollDrops().save(d, safe=True)
	deleteDrops(drops_to_remove)
	
def processStream(s, queue):
	try:
		fc = 0
		dc = 0
		tc = 0
		friendlist = {}
		#clog("starting")
		#if False:
		#	friendlist = {}
		#	for user in getCollUsers().find():
		#		if "id_str" in user:
		#			friendlist[int(user["id_str"])] = getCollDrops().find({"newsrivr_userid_md5":user["newsrivr_userid_md5"]}).distinct("user_id_str")
		#			s = set()
		#			for i in friendlist[int(user["id_str"])]:
		#				s.add(int(i))
		#			friendlist[int(user["id_str"])] = s   
		#			clog(user["screen_name"]+": "+str(len(friendlist[int(user["id_str"])])))	
		#
		show_message = False
		drops_to_delete = []		
		follow_messages_received = {}
		unfollow_messages_received = {}		
		if s:
			show_message = True
			user = s["for_user"]
			if "message" in s:
				if "friends" in s["message"]:
					clog("ignoring friends message")
					updateFriends(user, s["message"]["friends"])
					# ignore for now
					if False:
						newfriendlist = s["message"]["friends"]
						if user in friendlist:
							drops_from_old_friends = set(friendlist[user])-set(newfriendlist)
							for oldfriendid in drops_from_old_friends:
								deleteDropsForUser(user, oldfriendid)
						if user in friendlist:
							if newfriendlist!=friendlist[user]:
								friendlist[user] = None
							else:
								pass
								#clog("fiendlist the same")
						else:
							friendlist[user] = None
						if not friendlist[user]:
							friendlist[user] = newfriendlist
							updateFriends(user, newfriendlist)
						fc += 1
						#getCollStream().remove({"_id":s["_id"]}, safe=True)
				elif "delete" in s["message"]:
					try:
						if "status" in s["message"]["delete"]:
							d = getCollDrops().find_one({"id_str":s["message"]["delete"]["status"]["id_str"]})
							if not d:
								clog("drop does not exists")
							clog("delete drop")
							drops_to_delete.append(s["message"]["delete"]["status"]["id_str"])						
					except Exception, e:
						print e
					dc += 1					   
				elif "text" in s["message"] and "id_str" in s["message"]:
					#clog("new tweet")
					tc += 1								
					tweet = s["message"]
					tweet["inprocess"]=0
					tweet["for_user"] = user
					tweet["created_at"]=parse(tweet["created_at"]) 
					u = getUserByIDStr(user)
					if u:
						u = u["newsrivr_userid_md5"]
					if u:
						tweet["newsrivr_userid_md5"]=[u]
						insertTweet(tweet["id_str"], u, tweet)						
						#sender = s["message"]["user"]["id"]
						#user = getUserByMD5(u)
						#if user:
							#if sender in user["twitter_friend_list"]:
							#print "deze willen we"
							#insertTweet(tweet["id_str"], u, tweet)
							#else:
							#	pass
								#print "negeer deze maar"
					#getCollStream().remove({"_id":s["_id"]}, safe=True)
				elif "event" in s["message"]:
					if s["message"]["event"]=="user_update":
						if "target" in s["message"]:
							clog("profile update")
							updateProfile(user, s["message"]["target"])						
					elif s["message"]["event"]=="follow":
						if "source" in s["message"]:
							sourceuser = int(s["message"]["source"]["id_str"])
						if getUserByIDStr(sourceuser):
							if "target" in s["message"]:
								if sourceuser not in follow_messages_received:
									follow_messages_received[sourceuser] = set()
								if sourceuser in unfollow_messages_received:
									if s["message"]["target"]["id_str"] in unfollow_messages_received[sourceuser]:
										unfollow_messages_received[sourceuser].remove(s["message"]["target"]["id_str"])
								follow_messages_received[sourceuser].add(s["message"]["target"]["id_str"])
								clog(s["message"]["source"]["name"]+" follows "+s["message"]["target"]["name"])
					elif s["message"]["event"]=="unfollow":
						if "source" in s["message"]:
							sourceuser = int(s["message"]["source"]["id_str"])
						if getUserByIDStr(sourceuser):							
							if "target" in s["message"]:
								if sourceuser not in unfollow_messages_received:
									unfollow_messages_received[sourceuser] = set()
								if sourceuser in follow_messages_received:
									if s["message"]["target"]["id_str"] in follow_messages_received[sourceuser]:
										follow_messages_received[sourceuser].remove(s["message"]["target"]["id_str"])
								unfollow_messages_received[sourceuser].add(s["message"]["target"]["id_str"])
								clog(s["message"]["source"]["name"]+" unfollows "+s["message"]["target"]["name"])
					elif s["message"]["event"]=="favorite":						
						target_object_id_str = s["message"]["target_object"]["id_str"]
						d = getCollDrops().find_one({"id_str":target_object_id_str})
						if not d:
							d = getCollDrops().find_one({"retweet_id_str":target_object_id_str}) 
						if d:
							if "favorites" in d:
								d["favorites"].append(s["for_user"])
							else:
								d["favorites"] = [s["for_user"]]
							favs = []
							for i in d["favorites"]:
								favs.append(int(i))
							d["favorites"] = list(set(favs))
							clog("create favorite")
							getCollDrops().save(d, safe=True)
						else:
							clog("can't find this drop")
					elif s["message"]["event"]=="unfavorite":
						target_object_id_str = s["message"]["target_object"]["id_str"]
						d = getCollDrops().find_one({"retweet_id_str":target_object_id_str})
						retweet = False
						if d:
							if "favorites" in d:
								if s["for_user"] in d["favorites"]:
									retweet = True									
						if not d or not retweet:
							d = getCollDrops().find_one({"id_str":target_object_id_str})
						if d:
							if "favorites" in d:
								if s["for_user"] in d["favorites"]:
									d["favorites"].remove(s["for_user"])
									favs = []
									for i in d["favorites"]:
										favs.append(int(i))
									d["favorites"] = list(set(favs))
								clog("destroy favorite")
								getCollDrops().save(d, safe=True)
					elif "list_" in s["message"]["event"]:
						dlist = {}
						dlist["for_user"] = s["for_user"]
						dlist["event"] = s
						dtn, dtnms = getTimeWithMS()
						dlist["added_at"] = dtn
						dlist["added_at_precise"] = dtnms						
						if getCollLists().find({"for_user":s["for_user"], "event":s}).count()==0:
							getCollLists().save(dlist, safe=True)
					else:
						clog("ignoring:"+s["message"]["event"])
			subscribe(follow_messages_received)
			unsubscribe(unfollow_messages_received)
			drops_to_delete = list(set(drops_to_delete))
			deleteDrops(drops_to_delete)
			#clog(str(tc)+" text messages")
			#clog(str(fc)+" friends messages")
			#clog(str(dc)+" delete messages")
			if show_message:
				show_message = False
			#if getCollStream().count()==0:
				#print "sleeping"
			#	time.sleep(0.2)		
		queue.put(1)
	except (Exception), e:
		mailException(e)
	
def processStreamDriver():
	multiprocess = True
	# reset crashed tweets
	cnt = 0
	l = []
	queue = Queue()
	clog("checking for items in the stream queue: "+str(getCollStream().count()))
	while True:		
		s = getCollStream().find_one()
		if s:
			#delete_message = True
			#if "event" in s["message"]:
			#	if "list" in s["message"]["event"]:
			#		delete_message = False
			#if delete_message:
			getCollStream().remove({"_id":s["_id"]})
			cnt += 1		
			if cnt%5==0:
				clog(str(cnt)+" - "+str(len(l)))
			if multiprocess:
				clog("processing stream message")
				p = Process(target=processStream, args=(s, queue))				
				p.start()
				l.append(1)
			else:
				processStream(s, queue)
				queue.get()				
		else:
			clog("processStream: returned None!")
			return
		maxserver = 40
		#if "Darwin" in os.popen("uname").read():
		#	maxserver = 2
		if multiprocess:
			while len(l)>maxserver:
				queue.get()
				l.pop()

osname = None
def main():
	while True:
		try:
			processStreamDriver()
		except (Exception), e:
			mailException(e)
		global osname
		if not osname:
			osname = os.popen("uname").read()
		if "Darwin" in osname:		
			time.sleep(5)	

if __name__=="__main__":
	clog("streamworker online")
	driver(main, inspect.getfile(inspect.currentframe()))
