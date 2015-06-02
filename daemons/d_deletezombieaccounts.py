from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
#!/usr/bin/env python
from d_utils import *

def clog(s):
    s= str(s)
    print('\033[%93m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m')

def main():
	try:
		n = datetime.datetime.now()
		dt = timedelta(days=1)
		yesterday = n-dt
		crs = getCollUsers().find({"date_created":{"$lt": yesterday}})
		#crs = getCollUsers().find()
		clog("checking for zombieaccounts")
		cnt = 0
		for u in crs:
			if "twitter_credentials" not in u:
				cnt += 1
				getCollUsers().remove({"newsrivr_userid_md5":u["newsrivr_userid_md5"]}, safe=True)
		clog(str(cnt)+" zombies found")
	except (Exception) as e:
		mailException(e)

if __name__=="__main__":
    clog("checking for zombieaccounts")
    driver(main, inspect.getfile(inspect.currentframe()))
   
