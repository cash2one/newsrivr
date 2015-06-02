from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
#!/usr/bin/env python
import time
import pymongo
import pymongo.objectid
if "Darwin" in os.popen("uname").read():
	MONGOSERVER = 'localhost'
else:
	MONGOSERVER = '192.168.167.192'
	
MONGOPORT = 27017
from BeautifulSoup import BeautifulSoup, Comment
	
def getDB():
	conn = None
	while not conn:
		try:
			conn = pymongo.Connection(MONGOSERVER, MONGOPORT)
		except:
			time.sleep(1)
			print("no conn")
	db = conn.newsrivr
	return db

def getCollUsers():
	db = getDB()
	coll = db.users
	return coll

def getCollDrops():
	db = getDB()
	coll = db.drops
	return coll

def addReadmoreDivs():
	wcd = 0
	coll = getCollDrops().find()
	wcd = coll.count()
	savethesedrops = []
	for d in coll:
		print(wcd)
		wcd = wcd - 1
		#if 1==2:		
		for l in d["followed_links"]:
			html = ""
			shortened = False
			findclosetag = False
			wc = 0
			if "simplehtml" in l:		
				if 1==2:#"<table" in l["simplehtml"]:
					html += "<div id='hide_"+d["id_str"]+"' style='display:none;'>"
					html += l["simplehtml"]
					shortened = True
				else:
					splithtml = l["simplehtml"].split(" ")
					if len(splithtml)>100:
						for i in splithtml:
							html += i + " "
							wc += 1
							if wc>50 and not shortened and not findclosetag:
								findclosetag = True								
							if findclosetag:
								if "</p" in i and (len(splithtml)-wc)>50 and not shortened:
									shortened = True
									findclosetag = False
									html += "<div class='nr_contenthider' id='nr_hide_"+d["id_str"]+"' style='display:none;'>"
				if shortened:
					html += "</div><a id='nr_readmore_"+d["id_str"]+"' href='#' onclick='javascript:showContent(\""+d["id_str"]+"\"); return false;' style=\"float:right;\"><img src=\"/static/images/readmore.png\" alt=\"Read more\" border=\"0\" />Read more...</a>"
					l["simplehtml"] = html
					savethesedrops.append(d)
	for d in savethesedrops:				
		getCollDrops().save(d, safe=True)

def removeReadmoreDivs():
	wc = 0
	coll = getCollDrops().find()
	wc = coll.count()
	for d in coll:
		wc = wc - 1
		if wc%1000==0:
			print(wc)
		for l in d["followed_links"]:
			html = ""
			if "simplehtml" in l:
				soup = BeautifulSoup(l["simplehtml"])
				for tag in soup.findAll(True):
					if "id" in tag:
						if "hide_" in str(tag["id"]) and "nr_hide_" not in str(tag["id"]):
							print(wc, tag["id"])
							tag.hidden = True
						if "readmore_" in str(tag["id"])and "nr_readmore_" not in str(tag["id"]):
							tag.extract()
				html = soup.renderContents()
				l["simplehtml"] = html
				getCollDrops().save(d, safe=True)				
							
def test():
	html = """<p>Perdiep Ramesar &acirc;&agrave;&iacute; 23/02/11, 06:41</p>
<p><b>Nederland krijgt een Nationaal Cyber Security Centrum, waarin de overheid en het bedrijfsleven samenwerken aan cyberveiligheid. Dit is een nieuwe stap in de strijd tegen terroristen en criminelen die via computertechnologie hun slag slaan.</b></p>In het centrum komen de partijen&nbsp; bij elkaar om (dreigings)informatie,&nbsp; kennis en expertise uit te wisselen&nbsp; en te delen. Zo ontstaat &Atilde;&copy;&Atilde;&copy;n adres op&nbsp; dit terrein voor overheid en bedrijfsleven. Het centrum moet 1 januari&nbsp; 2012 operationeel zijn.
<p>Dat staat in de Nationale Cyber Security Strategie die minister Ivo Opstelten (VVD, veiligheid en justitie) gisteren heeft gepresenteerd.<br>
Naast dat centrum komt er ook een&nbsp; Cyber Security Raad. Die wordt het&nbsp; overlegorgaan rondom cyberveiligheid, waarin alle relevante partijen&nbsp; van de overheid en het bedrijfsleven&nbsp; zijn vertegenwoordigd.</p>
<div class="contenthider" id="hide_40304603522138112" style="">
    <p>Zodra er&nbsp; dreiging is, wordt dat besproken in&nbsp; de raad en wordt vanuit het centrum&nbsp; onderzocht en bekeken hoe op een&nbsp; cyberaanval moet worden gereageerd. De raad komt onder leiding&nbsp; van de Nationaal Co&Atilde;&para;rdinator Terrorismebestrijding Erik Akerboom namens de overheid, en namens het bedrijfsleven bestuursvoorzitter Eelco&nbsp; Blok van KPN. Met dit overlegorgaan&nbsp; wil de minister voorkomen dat verschillende organisaties langs elkaar&nbsp; heen werken.</p>
    <p>Bovendien komen bij de Nederlandse politie meer plekken om cybercriminaliteit aan te pakken.&nbsp; Daardoor verviervoudigt de capaciteit van het team hightech crime. Het&nbsp; gaat hierbij om grote ingewikkelde&nbsp; zaken die veel menskracht vergen.</p>
    <p>De aandacht voor cyberveiligheid&nbsp; is volgens de minister noodzakelijk,&nbsp; omdat computersystemen kwetsbaar worden, omdat ze door steeds&nbsp; meer mensen worden gebruikt. Criminelen en terroristen weten dat ze&nbsp; ook via de digitale weg de samenleving kunnen ontwrichten. Zo werd&nbsp; afgelopen weekend de website van&nbsp; de Rabobank overladen met grote&nbsp; hoeveelheden informatie. De website was daardoor tijdelijk onbereikbaar. De bank meldde gisteren aangifte van de cyberaanval te doen.</p>
    <p>Opstelten: "Door samenwerking&nbsp; kunnen we weerbaarder worden en&nbsp; ervoor zorgen dat we goed kunnen&nbsp; reageren op bijvoorbeeld cyberspionage, cybercrime, cyberterrorisme en&nbsp; cyberwarfare, maar ook verstoringen&nbsp; door technisch of menselijk falen."<br></p>
</div><a id="readmore_40304603522138112" href="#" onclick="javascript:showContent(&quot;40304603522138112&quot;); return false;" style="float: right; display: none;" name="readmore_40304603522138112"><img src="/static/images/readmore.png" alt="Read more" border="0">Read more...</a>
	"""
	soup = BeautifulSoup(html)
	for tag in soup.findAll(True):
		if "id" in tag:
			if "hide_" in str(tag["id"]) and "nr_hide_" not in str(tag["id"]):
				print(tag["id"])
				tag.hidden = True
			if "readmore_" in str(tag["id"])and "nr_readmore_" not in str(tag["id"]):
				tag.extract()
	html = soup.renderContents()
	print(html)
	
def main():
	#test()
	removeReadmoreDivs()
	#addReadmoreDivs()
	
if __name__ == '__main__':
	main()