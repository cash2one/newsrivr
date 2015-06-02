"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

	
from xml.sax.saxutils import escape

import urllib, re, os, urlparse
import HTMLParser, feedparser
from BeautifulSoup import BeautifulSoup, Comment
from pprint import pprint
import codecs
import sys
import htmlentitydefs
streamWriter = codecs.lookup("utf-8")[-1]
sys.stdout = streamWriter(sys.stdout)


HN_RSS_FEED = "http://news.ycombinator.com/rss"

negative_str = "([A-Z,a-z,0-9,-,_ ]*comments[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*comment[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*bcomments[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*meta[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*footer[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*footnote[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*foot[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*bottom[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*klasbox[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*side[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*inner[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*sidebar[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*hide[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*component[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*reactie[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*ad[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*ads[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*transcript[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*react[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*transcript[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*transcriptText[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*error[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*related[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*also[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*share[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*sideblock[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*policy[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*related[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*social[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*reflist[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*postmetadata[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*references[A-Z,a-z,0-9,-,_ ]*)|"
negative_str += "([A-Z,a-z,0-9,-,_ ]*promo[A-Z,a-z,0-9,-,_ ]*)"
NEGATIVE	= re.compile(negative_str)

super_negative_str = "([A-Z,a-z,0-9,-,_ ]*comment[A-Z,a-z,0-9,-,_ ]*)|"
super_negative_str += "([A-Z,a-z,0-9,-,_ ]*voting[A-Z,a-z,0-9,-,_ ]*)|"
super_negative_str += "([A-Z,a-z,0-9,-,_ ]*reactie[A-Z,a-z,0-9,-,_ ]*)|"
super_negative_str += "([A-Z,a-z,0-9,-,_ ]*reaction[A-Z,a-z,0-9,-,_ ]*)|"
super_negative_str += "([A-Z,a-z,0-9,-,_ ]*idgedragregelsusercontent[A-Z,a-z,0-9,-,_ ]*)|"
super_negative_str += "([A-Z,a-z,0-9,-,_ ]*vote[A-Z,a-z,0-9,-,_ ]*)"
SUPERNEGATIVE = re.compile(super_negative_str)

positive_str = "([A-Z,a-z,0-9,-,_ ]*summary[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*post[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*hentry[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*entry[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*content[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*text[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*tekst[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*venue[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*venueInfo[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*venueDetails[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*body[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*bodycontent[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*content permalink[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*wrapper[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*article[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*articleblock[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*text[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*tekst[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*lead[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*leadarticle[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*story[A-Z,a-z,0-9,-,_ ]*)|"
positive_str += "([A-Z,a-z,0-9,-,_ ]*permalink[A-Z,a-z,0-9,-,_ ]*)"

POSITIVE	= re.compile(positive_str)

PUNCTUATION = re.compile("""[!"#$%&\"()*+,-./:;<=>?@[\\]^_`{|}~]""")

MAXLINKS = 50


def latin1_to_ascii (unicrap):
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C',
        0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
        0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
        0xdd:'Y', 0xde:'th', 0xdf:'ss',
        0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
        0xe6:'ae', 0xe7:'c',
        0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
        0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
        0xf0:'th', 0xf1:'n',
        0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
        0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
        0xfd:'y', 0xfe:'th', 0xff:'y',
        0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 
        0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        0xd7:'*', 0xf7:'/'
        }
    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r

def toUTF8(data):
    try:
        data = data.encode("utf-8")
    except:
        data = latin1_to_ascii(data)
    return data

def text2simpleHtml(data):
	data = data.replace("<h1"," <b").replace("</h1>","</b><br><br>")
	data = data.replace("<h2"," <b").replace("</h2>","</b><br>")
	data = data.replace("<h3>","").replace("</h3>","<br>")
	
	VALID_TAGS = ["strong", "b", "i", "table", "th", "tr", "td", "a", "code", "em", "p", "ul", "li", "br"]
	soup = BeautifulSoup(data)
	for tag in soup.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True
	return soup.renderContents()

def _text(node):
	return " ".join(node.findAll(text=True))
	
def get_link_density(elem):
		link_length = len("".join([i.text or "" for i in elem.findAll("a")]))
		text_length = len(_text(elem))
		return float(link_length) / max(text_length, 1)

def removeFrontBreaks(s):
	try:
		soup = BeautifulSoup(s)
		whitespace = True
		for tag in soup.findAll(True):
			tagname = str(tag.name)
			if tagname!="br":
				whitespace=False
			if tagname!="p":
				whitespace=False                
			if tagname=="br" or tagname=="p" and whitespace:
				tag.extract()
		return str(soup).strip()
	except Exception, e:
		clog(e)
		return s

def convertentity(m): 
	"""Convert a HTML entity into normal string (ISO-8859-1)""" 
	if m.group(1)=='#': 
		try: 
			return chr(int(m.group(2))) 
		except ValueError: 
			return '&#%s;' % m.group(2) 
	try: 
		return htmlentitydefs.entitydefs[m.group(2)] 
	except KeyError: 
		return '&%s;' % m.group(2) 
def unquotehtml(s): 
	"""Convert a HTML quoted string into normal string (ISO-8859-1). 
	Works with &#XX; and with &nbsp; &gt; etc.""" 
	return re.sub(r'&(#?)(.+?);',convertentity,s) 

def getNumLinks(s):
	try:
		cnt = 0
		soup = BeautifulSoup(s)
		for a in soup.findAll("a"):
			if a.has_key("href"):
				#print a
				cnt += 1
		return cnt
	except:
		return 0

def removeEmptyParas(html):
	foundempty = False
	soup = BeautifulSoup(html)
	for p in soup.findAll("p"):
		if p.has_key("id"):
			if "error_" in p["id"]:
				p.extract()
		if 0==len(p.text.strip().replace("\n", "")):
			if foundempty:
				p.extract()
			foundempty = True
		else:
			foundempty = False
	return soup.renderContents()

def removeEmptyLis(html):
	soup = BeautifulSoup(html)
	for li in soup.findAll("li"):
		for a in li.findAll("a"):
			if len(a.contents)>0:
				if len(a.contents[0])<5:
					a.extract()
		if len(li.renderContents().strip())==0:
			li.extract()
		else:
			for x in li.findAll():
				if len(x.renderContents().strip())==0:
					li.extract()			
	for ul in soup.findAll("ul"):
		if 0==len(ul.findAll("li")):
			ul.extract()
	return soup.renderContents()
	
def removeExtraBreaks(s):
	try:
		l = []
		brcnt = 0
		soup = BeautifulSoup(s)
		for tag in soup.findAll():
			if tag.name=="p":
				if len(tag.text.strip().replace("\n", ""))<1:
					tag.extract()
					brcnt += 1
			if tag.name=="br":				
				brcnt += 1
				if brcnt>1:
					tag.extract()
			else:
				brcnt = 0
		return str(soup)
	except Exception, e:
		clog(e)
		return s

def grabContent(link, html):
		
	if "&gt;" in html:
		html = unquotehtml(html)
		
	html = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head><body>"+html+"</body></html>"
	#open("usedforscoring.html", "w").write(html)
	#exit(1)
	
	replaceBrs = re.compile("<br */? *>[ \r\n]*<br */? *>")
	html = re.sub(replaceBrs, "</p><p>", html)

	try:
		soup = BeautifulSoup(html)
	except HTMLParser.HTMLParseError, e:
		try:
			soup = BeautifulSoup(text2simpleHtml(html))
		except HTMLParser.HTMLParseError:
			return ""

	#print str(soup)	
	# REMOVE SCRIPTS	
	for s in soup.findAll("div"):
		if get_link_density(s)>0.5 and len(s.renderContents())>1000:
			s.extract()
		if s.has_key("id"):
			if SUPERNEGATIVE.match(str(s["id"]).lower()):
				s.extract()
		if s.has_key("class"):
			if SUPERNEGATIVE.match(str(s["class"]).lower()):
				s.extract()

	for s in soup.findAll("script"):
		s.extract()
		
	for a in soup.findAll("a"):
		if a.has_key("href"):
			if "javascript:" in a["href"]:
				a.extract()
		if a.has_key("onclick"):
			if "return " in a["onclick"]:
				a.extract()
	
	allParagraphs = soup.findAll("p")
	
	topParent	 = None
	
	parents = []
	
	for paragraph in allParagraphs:		
		parent = paragraph.parent			
		if (parent not in parents):
			parents.append(parent)
			parent.score = 0

			if (parent.has_key("class")):
				if (NEGATIVE.match(parent["class"].lower())):
					#print parent["class"]
					if len(parent.findAll('a'))>MAXLINKS:
						parent.score -= 500					
					parent.score -= 50
				if (POSITIVE.match(parent["class"].lower())):
					if len(parent.findAll('a'))<MAXLINKS:
						parent.score += 25
					else:
						parent.score -= 150
					parent.score += 50
					
			if (parent.has_key("id")):
				if (NEGATIVE.match(parent["id"].lower())):
					#print parent["id"]
					if len(parent.findAll('a'))>MAXLINKS:
						parent.score -= 500
					parent.score -= 50
				if (POSITIVE.match(parent["id"].lower())):
					if len(parent.findAll('a'))<MAXLINKS:
						parent.score += 25
					else:
						parent.score -= 150
					parent.score += 50
					
		if (parent.score == None):
			parent.score = 0
		
		innerText = paragraph.renderContents() #"".join(paragraph.findAll(text=True))
		if (len(innerText) > 10):
			parent.score += 1
		if (len(innerText) > 300):
			parent.score += 2
			
		parent.score += innerText.count(",")*3
		parent.score += innerText.count(".")*3
		
	for parent in parents:
		#print parent.score
		#print str(parent )
		#print "-------------"
		if ((not topParent) or (parent.score > topParent.score)):
			topParent = parent
			
	if (not topParent):
		return ""
		
	# REMOVE LINK"D STYLES
	styleLinks = soup.findAll("link", attrs={"type" : "text/css"})
	for s in styleLinks:
		s.extract()

	# REMOVE ON PAGE STYLES
	for s in soup.findAll("style"):
		s.extract()
	
	# CLEAN STYLES FROM ELEMENTS IN TOP PARENT
	for ele in topParent.findAll(True):
		del(ele["style"])
		del(ele["class"])
		#print str(ele)
		#print "-----"
		
	killDivs(topParent)
	clean(topParent, "form")
	clean(topParent, "object")
	clean(topParent, "iframe")
	
	fixLinks(topParent, link)
	
	for s in topParent.findAll("ul"):		
		if get_link_density(s)>0.3:
			s.extract()
			
	lis = topParent.findAll("li")
	if len(lis)>50:
		for li in lis:
			li.extract()
	for li in lis:
		if len(li)>1:
			contents = str(li.contents[1]).replace("\n", "").replace("&nbsp;", "").replace("<br>", "").replace("<br/>", "").replace("<br />", "").replace("<p></p>", "")
			#print "c", contents
			if len(contents)==0:
				li.extract()
			
	comments = topParent.findAll(text=lambda text:isinstance(text, Comment)) 
	[comment.extract() for comment in comments]
	
	html2 = topParent.renderContents()
	html2 = removeFrontBreaks(html2)
	html2 = html2.replace("\n", " ")

	for i in range(0, 10):
		html2 = html2.replace("  ", " ")	
		html2 = html2.replace("<div></div>", "")
		html2 = html2.replace("<p>\xc2\xa0</p>", "")
		html2 = html2.replace("<p></p>", "<br/>")
		html2 = html2.replace("<p><br /></p>", "")
	
	#html2 = html2.replace("\xc2\xa9", "")#
	html2 = re.sub(r'&copy; (\w+.\w+)', "", html2)
	html2 = re.sub(r'&copy; (\w+)', "", html2)	
	html2 = re.sub(r'\xc2\xa9 (\w+.\w+)', "", html2)
	html2 = re.sub(r'\xc2\xa9 (\w+)', "", html2)

	#if getNumLinks(html2)>25:
	#		html2 = "html ignored, more then 25 links"
		
	#print get_link_density(BeautifulSoup(html2))
	html2 = removeEmptyLis(html2)
	html2 = toUTF8(text2simpleHtml(html2)).replace("a href", "a target='blank' href")
	html2 = removeEmptyParas(html2)	
	html2 = removeExtraBreaks(html2)
	html2 = html2.replace("</strong>", "</strong><br/>")
	html2 = html2.replace("</b>", "</b><br/>")
	
	#detect
	return html2
	
def fixLinks(parent, link):
	tags = parent.findAll(True)	
	for t in tags:
		if (t.has_key("href")):
			t["href"] = urlparse.urljoin(link, t["href"])
		if (t.has_key("src")):
			t["src"] = urlparse.urljoin(link, t["src"])

def clean(top, tag, minWords=10000):
	tags = top.findAll(tag)
	for t in tags:
		if (t.renderContents().count(" ") < minWords):
			t.extract()

def killDivs(parent):	
	divs = parent.findAll("div")
	for d in divs:
		p	 = len(d.findAll("p"))
		img   = len(d.findAll("img"))
		li	= len(d.findAll("li"))
		a	 = len(d.findAll("a"))
		embed = len(d.findAll("embed"))
		pre   = len(d.findAll("pre"))
		#code  = len(d.findAll("code"))
	
		if (d.renderContents().count(",") < 10):
			if (pre == 0):# and (code == 0)):
				if ((img > p ) or (li > p) or (a > p) or (p == 0) or (embed > 0)):
					d.extract()					

def upgradeLink(link):
	link = link.encode("utf-8")	
	if (not (link.startswith("http://news.ycombinator.com") or link.endswith(".pdf"))):
		linkFile = "upgraded/" + re.sub(PUNCTUATION, "_", link)
		if (os.path.exists(linkFile)):
			return open(linkFile).read()
		else:
			content = ""
			try:
				html = urllib.urlopen(link).read()
				content = grabContent(link, html)
				filp = open(linkFile, "w")
				filp.write(content)
				filp.close()
			except IOError:
				pass
			return content
	else:
		return ""
	
	

def upgradeFeed(feedUrl):	
	feedData = urllib.urlopen(feedUrl).read()	
	upgradedLinks = []
	parsedFeed = feedparser.parse(feedData)	
	for entry in parsedFeed.entries:
		upgradedLinks.append((entry, upgradeLink(entry.link)))
	rss = """<rss version="2.0">
	<channel>
	<title>Hacker News</title>
	<link>http://news.ycombinator.com/</link>
	<description>Links for the intellectually curious, ranked by readers.</description>	 
	"""
	for entry, content in upgradedLinks:
		rss += u"""
	<item>
		<title>%s</title>
		<link>%s</link>
		<comments>%s</comments>
		<description>
			<![CDATA[<a href="%s">Comments</a><br/>%s<br/><a href="%s">Comments</a>]]>
		</description>
	</item>
""" % (entry.title, escape(entry.link), escape(entry.comments), entry.comments, content.decode("utf-8"), entry.comments)
	rss += """
</channel>
</rss>"""
	return rss

def clog(s):
	from time import gmtime, strftime
	s= str(s)
	print '\033[%93m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m'

if __name__ == "__main__":	
	c = open("usedforscoring.html", "r").read()
	soup = BeautifulSoup(grabContent('x', c))
	clog(soup.prettify())
