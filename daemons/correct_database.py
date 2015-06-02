from d_utils import *

def doubles():
	#print "DISABLED!!!"
	#return
	cnt2 = 0
	cnt = getCollDrops().count()
	for d in getCollDrops().find():
		if cnt%1000==0:
			print "removing doubles:", cnt
		cnt = cnt -1
		for i in getCollDrops().find({"id_str":d["id_str"]}):
			if i["_id"]!=d["_id"]:
				d["newsrivr_userid_md5"].extend(i["newsrivr_userid_md5"])
				d["newsrivr_userid_md5"] = list(set(d["newsrivr_userid_md5"]))		
				getCollDrops().remove({"_id":pymongo.objectid.ObjectId(i["_id"])}, safe=True)
				getCollDrops().save(d, safe=True)
				cnt2 = cnt2 + 1

	print cnt2, "corrected"

def deleteImageYoutube(dropids):
	cnt = len(dropids)
	if cnt==0:
		return
	s = "["
	for did in dropids:
		s += "{'id_str':'"+did+"'},"
		cnt = cnt - 1
	s += "]"
	s = s.replace(",]", "]")
	s = eval(s)
	
	yt = getCollYoutubeTags().find({ "$or" : s}).count()
	imd5 = getCollImageMd5s().find({ "$or" : s}).count()
	
	getCollYoutubeTags().remove({ "$or" : s}, safe=True)
	getCollImageMd5s().remove({ "$or" : s}, safe=True)
	
	return 

def trimTweetsPerUser():
	twitters = {}
	dropids = []	
	for user_id_str in getCollDrops().find().distinct("user_id_str"):
		dropcount = getCollDrops().find({"user_id_str":user_id_str}).count()
		if dropcount>52:		
			u = getCollDrops().find_one({"user_id_str":user_id_str})			
			created_at = None
			#d = getCollDrops().find_one({"user_id_str":user_id_str})
			cnt = 0
			for d in getCollDrops().find({"user_id_str":user_id_str, "favorites":{'$exists':False}}, sort=[("created_at", -1)]):				
				if cnt>50:
					created_at = d["created_at"]
					print dropcount, u["user"]["screen_name"], created_at

					for i in getCollDrops().find({"user_id_str":user_id_str, "favorites":{'$exists':False}, "created_at":{"$lt": created_at}}):
						dropids.append(i["id_str"])					
					getCollDrops().remove({"user_id_str":user_id_str, "favorites":{'$exists':False}, "created_at":{"$lt": created_at}}, safe=True)
					break
				cnt = cnt + 1
	deleteImageYoutube(dropids)	
	return

def deleteEmptyFavorites():
	cnt = 0
	for d in getCollDrops().find({"favorites":{'$exists':True}}):
		#print cnt, d["id_str"]
		if "favorites" in d:
			if len(d["favorites"])==0:
				getCollDrops().remove({"id_str":d["id_str"]}, safe=True)
				print "removed", cnt, d["id_str"]
		cnt += 1

def addThumbnailBase64():
	images = {}
	delete_all = False
	if delete_all:
		for d in getCollDrops().find({"profile_image_url_big_base64":{'$exists':True}}):
			del d["profile_image_url_big_base64"]
			del d["profile_image_url_small_base64"]
			getCollDrops().save(d, safe=True)
	cnt = getCollDrops().find({"profile_image_url_big_base64":{'$exists':False}}).count()
	print "numdrops:",cnt			
	clog("making cache")			
	for d in getCollDrops().find({"profile_image_url_big_base64":{'$exists':True}}):
		bt = d["user"]["profile_image_url"].replace("_normal", "_reasonably_small")
		images[bt] = (d["profile_image_url_big_base64"], d["profile_image_url_small_base64"])		
	clog("making thumbnails")
	for d in getCollDrops().find({"profile_image_url_big_base64":{'$exists':False}}):
		bt = d["user"]["profile_image_url"].replace("_normal", "_reasonably_small")
		cnt -= 1;
		if cnt%50==0:
			print cnt, bt
		if bt not in images:
			try:
				data = urllib.urlopen(bt).read()
				fdata = cStringIO.StringIO(data)
				i = Image.open(fdata)
			except (Exception), e:
				print e
				data = urllib.urlopen(d["user"]["profile_image_url"]).read()
				fdata = cStringIO.StringIO(data)
				i = Image.open(fdata)
			if float(i.size[1]) / float(i.size[0])>0.5:
				if cnt%10==0:
					print d["screen_name"], bt					
				nh = float(i.size[1]) / float(i.size[0]) * 80			
				i = i.resize((80, int(nh)),Image.ANTIALIAS)
				outdata = cStringIO.StringIO()
				bts = bt.split(".")
				format = bts[len(bts)-1].lower()			
				if format=="jpg":
					format = "jpeg"
				if format!="jpeg" and format!="png" and format!="gif":
					pass
				else:
					i.save(outdata, format)
					d["profile_image_url_big_base64"] = "data:image/"+format+";base64,"+base64.encodestring(outdata.getvalue())
					nh = float(i.size[1]) / float(i.size[0]) * 30
					i = i.resize((30, int(nh)),Image.ANTIALIAS)
					outdata = cStringIO.StringIO()
					i.save(outdata, format)		
					d["profile_image_url_small_base64"] = "data:image/"+format+";base64,"+base64.encodestring(outdata.getvalue())
					images[bt] = (d["profile_image_url_big_base64"], d["profile_image_url_small_base64"])
			else:
				print "skipping:", float(i.size[1]) / float(i.size[0]), bt
		else:
			if cnt%10==0:			
				print d["screen_name"]
			d["profile_image_url_big_base64"] = images[bt][0]
			d["profile_image_url_small_base64"] = images[bt][1]
		getCollDrops().save(d, safe=True)
		#if bt not in images:
		#	images[bt] = 
	

def correctDrops():
	coll = getCollDrops().find({"retweet_created_at":{'$exists':True}})
	cnt2 = cnt = coll.count()
	tosave = []
	for d in coll:
		try:
			d["retweet_created_at"] = parse(d["retweet_created_at"])
		except:
			pass		
		tosave.append(d)
		if cnt%100==0:
			print cnt
		cnt -= 1
	for d in tosave:
		getCollDrops().save(d, safe=True)
		if cnt2%100==0:
			print cnt2
		cnt2 -= 1


def add_precise_added_at():
	cnt = 0
	#db.drops.find({"added_at_precise":{$gt:1304576821.0}}, {'added_at_precise':1, "added_at":1}).count()
	coll = getCollDrops().find({"added_at_precise":{'$lt':1304598421.0}, 'newsrivr_userid_md5': 'b4cbd625a37ae741747c89f68b281998'}, sort=[("added_at_precise", -1)]).limit(400)
	print coll.count(), "left"
	l = []
	for d in coll:
		if cnt%100==0:
			print cnt
		cnt = cnt + 1;
		d["added_at_precise"] = time.mktime(d["created_at"].utctimetuple())
		l.append(d)
	print len(l)
	for d in l:
		getCollDrops().save(d, safe=True)
		cnt = cnt - 1
		if cnt%100==0:
			print cnt

def correctYoutubeKeys():
	for k in getCollYoutubeTags().find():
		if len(k['videotag'])>12:
			getCollYoutubeTags().remove(k, safe=True)

def main():
	deleteEmptyFavorites()
	trimTweetsPerUser()	
	correctYoutubeKeys()
	
def checkIfRunning():
    fn = str(inspect.getfile( inspect.currentframe())).replace(".py", ".pid")
    try:
        f = open(fn, "w")
        portalocker.lock(f, portalocker.LOCK_EX|portalocker.LOCK_NB)
        timestamp = time.strftime("%m/%d/%Y %H:%M:%S\n", time.localtime(time.time()))
        f.write(timestamp)
        f.write(str(os.getpid())+"\n")
        return f
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        return None

def driver():
    lf = checkIfRunning()
    if not lf:
        return
    cf = inspect.getfile(inspect.currentframe())
    ks = str(cf).replace(".py", "")+"kill.sh"
    open(ks, "w").write("kill "+str(os.getpid())+"\nrm "+ks+"\n")
    os.system("chmod +x "+ks)
    main()
    try:
        pass
    except (KeyboardInterrupt, SystemExit):
        os.system("rm "+ks)
    except Exception, e:
        print e
        os.system("rm "+ks)
    lf.close()
    os.remove(lf.name)
                
if __name__=="__main__":
    clog("correct database")
    #main()
    driver()