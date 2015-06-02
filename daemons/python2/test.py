from __future__ import print_function

from d_utils import *

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

def main():
	user = getCollUsers().find_one({"screen_name":"Scobleizer"})
	slugs = []
	for i in user['lists']:
		slugs.append(i["slug"])
	
	for slug in slugs:
		print(slug)
		ulist = slug #"tech-companies"
		coll = getCollDrops()
		lst = getIdsList(user, ulist)
		orquery = listToMongoOr(lst, "created_by")			
		dcoll = coll.find({"$or":eval(orquery), "newsrivr_userid_md5":user["newsrivr_userid_md5"], "added_at_precise":{"$lt": 1308122797.6256001} }, sort=[("added_at_precise", -1)])
		print(dcoll.count())
	
	#for i in dcoll:
	#	print i
	
if __name__=="__main__":
	main()