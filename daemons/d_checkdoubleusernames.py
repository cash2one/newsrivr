
from d_utils import *

def clog(s):		
	s= str(s)
	print '\033[%96m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m'

def checkDoubleUsernames(exis_user_screen_name):
	users_same_name = []
	# find out if there are more users with the same screenname, this can happen after an deny.
	crs = getCollUsers().find({"screen_name":exis_user_screen_name}, sort=[("date_created", 1)])
	for i in crs:
		users_same_name.append(i)
	
	#TODO dit checken tegen d_sitenewusers
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
	else:
		return
		
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
						if getCollDrops().find(d).count()>0:
							getCollDrops().remove(d, safe=True)
						else:							
							getCollDrops().save(d, safe=True)
				deleteDrops(drops_to_remove)
				
def main():
	while True:
		for u in getCollUsers().find():
			if "screen_name" in u:
				checkDoubleUsernames(u["screen_name"])
		time.sleep(20)
		
if __name__=="__main__":
	clog("check if double names exists")			
	driver(main, inspect.getfile(inspect.currentframe()))
