import csv
import json
import pymongo
from pymongo.objectid import ObjectId
from pymongo import Connection

def import_feeds():
    print "reading"
    s = set()
    r = csv.reader(open("feeds.txt", "rU"))
    for i in r:
        if len(i)>1:
            if len(i[1])>0:
                s.add(i[1])
    connection = Connection()
    connection = Connection("localhost", 27017)
    db = connection.river
    collection = db.spider
    print "inserting"
    for i in s:
        feed = { "url" : i}
        collection.feeds.insert(feed)
        
def find_feeds():
    connection = Connection("192.168.0.18", 10000)
    db = connection.river
    collection = db.spider
    d = {}
    l = ["hello", "world"]
    d["data"] = l
    print json.dumps(d)
    db.testtable.insert(d)
    
def main():
    #find_feeds()
    
    connection = Connection("kain.active8.nl", 10000,  slave_okay=True)
    db = connection.river
   
    for o in db.testtable.find():
        print o
    
    #
    
if __name__=="__main__":
    main()
    print "ok"