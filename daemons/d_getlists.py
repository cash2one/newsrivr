
from d_utils import *
import twitter

def clog(s):		
	s= str(s)
	print '\033[%96m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m'
	
def robustFetch(u):
	for i in range(0,5):
		try:
			c = fetch(u)
			if "data" in c:
				return c
		except:
			clog("fetch error waiting 10 seconds")
			time.sleep(10)

def walkLists(user):
	lists = []
	if "lists" in user:
		if "lists" in user["lists"]:			
			for l in user["lists"]["lists"]:
				list = {}
				list["id"] = l["id"]
				list["name"] = l["name"]
				list["slug"] = l["slug"]
				list["members"] = []
				for m in l["members"]["users"]:
					list["members"].append(m["id_str"])
				lists.append(list)
	user["lists"] = lists
	return user

def downloadLists(user):
	#users.append(getCollUsers().find_one({"screen_name":"rabshakeh"}))
	if "access_token" in user and "twitter_credentials" in user:
		c = robustFetch("http://api.twitter.com/1/lists.json?screen_name="+user["screen_name"])			
		if "data" in c:								
			clog("fetching lists for: "+user["screen_name"])
			user["lists"] = simplejson.loads(c["data"])
			if "error" in user["lists"]:
				return False
			if "lists" in user["lists"]:
				for l in user["lists"]["lists"]:
					cl = robustFetch("http://api.twitter.com/1/lists/members.json?list_id="+l["id_str"])
					if "data" in cl:
						l["members"] = simplejson.loads(cl["data"])							
		else:
			if "lists" in user:
				del user["lists"]
	user = walkLists(user)					
	getCollUsers().save(user)
	return True

def optimizeListStructureWithDropSlugs(user):
	if "lists" in user.keys():
		if "error" in user["lists"]:
			time.sleep(60)
			return False
		for l in user["lists"]:
			for m in l["members"]:
				cnt = 0
				for d in getCollDrops().find({"created_by":m, "newsrivr_userid_md5":user["newsrivr_userid_md5"]}):
					cnt += 1
					savethis = True
					if "list_slugs" in d:
						if l["slug"] in d["list_slugs"]:
							savethis = False
						d["list_slugs"].append(l["slug"])
					else:
						d["list_slugs"] = [l["slug"]]
					d["list_slugs"] = list(set(d["list_slugs"]))
					if savethis:
						getCollDrops().save(d, safe=True)
	return True

def removeSlugFromDropForTarget(slug, target):
	for d in getCollDrops().find({"list_slugs":slug, "user_id_str":target}):
		d["list_slugs"].remove(slug)
		getCollDrops().save(d, safe=True)
		
def addSlugToDropForTarget(slug, target):
	for d in getCollDrops().find({"user_id_str":target}):		
		if "list_slugs" in d:
			d["list_slugs"].append(slug)
		else:
			d["list_slugs"] = [slug]
		d["list_slugs"] = list(set(d["list_slugs"]))
		getCollDrops().save(d, safe=True)

def main(oneTime=False):
	#optimizeListStructureWithDropSlugs()
	#return
	while True:
		clog("checking lists")
		users_new_listitems = []
		clists = []
		for i in getCollLists().find(sort=[("added_at_precise", -1)]):
			user = getCollUsers().find_one({"id_str":str(i["for_user"])})			
			if i["event"]:			
				slug = i["event"]["message"]["target_object"]["slug"]
				target = i["event"]["message"]["target"]["id_str"]
				if i["event"]["message"]["event"]=="list_member_removed":
					removeSlugFromDropForTarget(slug, target)
					clists.append(i)				
				elif i["event"]["message"]["event"]=="list_member_added":
					addSlugToDropForTarget(slug, target)
					clists.append(i)
				elif i["event"]["message"]["event"]=="list_updated":
					slug = i["event"]["message"]["target_object"]["slug"]
					list_id = i["event"]["message"]["target_object"]["id"]
					oldslug = None
					if "lists" in user:
						for l in user["lists"]:
							if l["id"]==list_id:
								oldslug = l["slug"]
								l["slug"]=slug
								l["name"]=i["event"]["message"]["target_object"]["name"]
					if oldslug:						
						for d in getCollDrops().find({"list_slugs":oldslug, "newsrivr_userid_md5":user["newsrivr_userid_md5"]}):							
							d["list_slugs"].remove(oldslug)
							d["list_slugs"].append(slug)
							getCollDrops().save(d, safe=True)
					getCollUsers().save(user, safe=True)
					clists.append(i)
				else:
					downloadLists(user)
					if optimizeListStructureWithDropSlugs(user):
						clists.append(i)
			else:
				downloadLists(user)
				if optimizeListStructureWithDropSlugs(user):
					clists.append(i)				
		for i in clists:
			getCollLists().remove({"_id":pymongo.objectid.ObjectId(i["_id"])}, safe=True)
		if oneTime:
			return
		else:
			time.sleep(10)

def upgradeAllUserListRecords():
	for user in getCollUsers().find():
		if "screen_name" in user:
			downloadLists(user)
			optimizeListStructureWithDropSlugs(user)
	
if __name__=="__main__":
	#upgradeAllUserListRecords()
	#clog("get lists for users")
	#main(True)
	driver(main, inspect.getfile(inspect.currentframe()))
