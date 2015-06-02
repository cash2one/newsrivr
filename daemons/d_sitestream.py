
from d_utils import *

def clog(s):
	s= str(s)
	print '\033[%95m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m'
	
class Client:
	def __init__(self, users):
		self.friends = []
		self.buffer = ""
		self.userid = None
		self.conn = pycurl.Curl()
		self.users = users
				
	def connect(self):
		self._signature = OAuthSignatureMethod_HMAC_SHA1()
		self._consumer = OAuthConsumer(consumer_key,
									   consumer_secret)
		self._access_token = OAuthToken(access_token,
										access_token_secret)
		#print self.users
		params = {
			'follow': self.users,
			"with":"followings"
			}
		oauth_request = OAuthRequest.from_consumer_and_token(
											self._consumer,
											token=self._access_token,
											http_method='GET',
											http_url=STREAM_URL,
											parameters=params)
		#print oauth_request.to_url()
		headers = oauth_request.to_header()
		oauth_request.sign_request(self._signature,
								   self._consumer,
								   self._access_token)	
		self.conn.setopt(pycurl.URL, oauth_request.to_url())
		self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
		self.conn.perform()
	
	def storeStream(self, d):
		try:
			clog("message received")
			if "message" in d:
				if "created_at" in d["message"]:
					d["created_at"] = d["message"]["created_at"]
				else:
					d["created_at"]=datetime.datetime.now()
			else:
				d["created_at"]=datetime.datetime.now()
			if not getCollStream().find_one(d):
				getCollStream().insert(d, safe=True)
			else:
				clog("got message already")
		except (Exception), e:
			mailException(e)
			
	def recurse_splits(self, d):
		ds = d.split("\r\n")
		if len(ds)==1:			
			d = ds[0].strip()
			if len(d)>0:
				d = simplejson.loads(d)
				self.storeStream(d)
			return
		for d in ds:
			self.recurse_splits(d)

	def on_receive(self, data):
		if "UNAUTHORIZED" in data:
			print data
		self.buffer += data
		if data.endswith("\r\n") and self.buffer.strip():
			self.recurse_splits(self.buffer)
			self.buffer = ''
				
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
		clog("already running")
		#traceback.print_exc(file=sys.stdout)
		return None

class ClientT(multiprocessing.Process):
	def __init__(self, users):
		multiprocessing.Process.__init__(self)
		self.client = Client(users)
	def run(self):
		clog("client starts")
		self.client.connect()
		
def killSubProcess():
	for i in os.popen("ps ax | grep "+inspect.getfile(inspect.currentframe())):
		i_s = str(i).lower().replace("\n", "").strip()
		for i in range(0,20):
			i_s = i_s.replace("  ", " ")
		if "python" in i_s:
			i_ss = i_s.split(" ")
			if len(i_ss)>0:
				ppid = i_ss[0]
				if ppid!=str(os.getpid()):
					os.system("kill "+ppid)
		
class ReconnectMonitor(multiprocessing.Process):
	def __init__(self):
		multiprocessing.Process.__init__(self)
	def run(self):
		last_check_users = None
		starttime = time.time()
		client1 = True
		while True:
			check_users = []
			for u in getCollUsers().find():
				if "id_str" in u:
					check_users.append(u["id_str"])
			users_to_stream=str(check_users).replace("u", "").replace("'", "").replace("[", '').replace("]", '').replace(" ", "")			
			if not last_check_users:
				last_check_users = users_to_stream
				self.client = ClientT(last_check_users)
				self.client.start()				
			else:
				reboot = False
				if last_check_users != users_to_stream:
					reboot = True
					last_check_users = users_to_stream
				runningtime = time.time()-starttime
				#clog(runningtime)
				if runningtime>900:
					starttime = time.time()
					reboot = True
				if reboot:
					reboot = False
					clog("kill client and reconnect")
					if client1:
						client1 = False
						self.client2 = ClientT(last_check_users)
						self.client2.start()
						time.sleep(30)
						self.client.terminate()
					else:
						client1 = True
						self.client = ClientT(last_check_users)
						self.client.start()
						time.sleep(30)
						self.client2.terminate()
			#print os.popen("ps aux | grep Python").read()
			time.sleep(10)

def driver():
	lf = checkIfRunning()
	if not lf:
		return
	cf = inspect.getfile(inspect.currentframe())
	ks = str(cf).replace(".py", "")+"kill.sh"
	open(ks, "w").write("kill "+str(os.getpid())+"\nrm "+ks+"\n")
	os.system("chmod +x "+ks)
	rm = ReconnectMonitor()	
	try:
		rm.start()
		rm.join()
	except (KeyboardInterrupt, SystemExit):
		os.system("rm "+ks)
		rm.terminate()
		killSubProcess()	   
	except Exception, e:
		print e
		os.system("rm "+ks)
	lf.close()
	os.remove(lf.name)
	killSubProcess()
	
if __name__=="__main__":
	clog("sitestream daemon online")
	driver()