#!/usr/bin/env pythonimport os
from d_utils import *

def getDB():
	cnt = 0
	db = None
	try:
		conn = pymongo.Connection(MONGOSERVER, MONGOPORT)
		db = conn.newsrivr
		return db
	except:
		return None
			
def main():
	if not getDB():
		os.system("killall mongod")		
		os.remove("/home/rabshakeh/mongodb/mongod.lock")
		os.system("/home/rabshakeh/mongodb-linux-x86_64-1.8.2-rc2/bin/mongod --journal --dbpath /home/rabshakeh/mongodb/  --fork --logpath /dev/null --bind_ip 192.168.167.192")
		time.sleep(600)

if __name__ == '__main__':
	driver(main, inspect.getfile(inspect.currentframe()))