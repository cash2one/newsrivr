#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
from d_utils import *

def clog(s):
    s= str(s)
    print('\033[%93m'+strftime("%Y-%m-%d %H:%M:%S", gmtime())+": "+s+'\033[%0m')

def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return text

def linkList(text):
    text = text.replace("'", "").replace('"', '')
    l = []
    for li in re.finditer( r"(http://[^ ]+)", text ):
        l.append(text[li.span()[0]:li.span()[1]])
    for li in re.finditer( r"(https://[^ ]+)", text ):
        l.append(text[li.span()[0]:li.span()[1]])
    l2 = []
    for i in l:
        if i not in l2:
            l2.append(i)
    return l2
    
def isImage(imglink):
    try:
        file = urllib.request.urlopen(imglink)
        im = cStringIO.StringIO(file.read()) # constructs a StringIO holding the image
        i = Image.open(im)
        return True
    except Exception as e:
        return False

def getSizeInMB(url):
    try:
        request = urllib.request.Request(url)
        opener = urllib.request.build_opener()
        firstdatastream=opener.open(request)
        size = -1
        size = old_div(float(firstdatastream.headers.dict["content-length"]),1000000)
        return size
    except (Exception) as ex:
        return -1

def getContentWget(u):
    content = {}
    content["status"] = 404
    t1 = NamedTemporaryFile(delete=False)
    t1.close()
    os.system("wget -q '"+u+"' -O "+t1.name)
    c = open(t1.name, "r").read()
    os.remove(t1.name)
    if len(content)>0:
        content["url"] = u
        content["status"] = 200
        content["data"] = c
    return content
    
def fetch2(u):    
    content = {}
    content["status"] = 404
    h = urllib.request.urlopen(u).headers.headers
    s = urllib.request.urlopen(u)
    content["url"] = s.geturl()
    content["status"] = s.getcode()
    content["data"] = s.read()
    return content
    
def ishtml(html):
    clog("ishtml")
    try:
        soup = BeautifulSoup(html)
        if len(soup.findAll(True))>2:
            return True
    except:
        clog("ishtml error")
    return False
    
def findLinks(text):
    ll = []
    l = linkList(text)
    for lk in l:
        try:
            if "tcrn.ch" in str(lk):
                #time.sleep(60)
                pass                    
            if getSizeInMB(lk)<3:
                d = {'url':lk}
                try:
                    d = fetch(lk)
                    if ";URL=" in d["data"]:
                        for meta in BeautifulSoup(d["data"], parseOnlyThese=SoupStrainer("meta")):
                            meta = str(meta)
                            meta = meta.split("URL=")
                            if len(meta)>1:
                                meta = meta[1].split('"')
                            if len(meta)>1:
                                d = fetch(meta[0])
                    if "?url=" in str(d["url"]):
                        slk = d["url"].split("?url=")
                        lk = slk[len(slk)-1]
                        d = fetch(lk)                    
                    if not ishtml(d["data"]):
                        d = fetch2(lk)
                        if not ishtml(d["data"]):
                            d = getContentWget(lk)
                            if not ishtml(d["data"]):
                                clog("alleen maar crap returning")
                                return ll
                except Exception as e:
                    clog(e)
                    try:
                        d = fetch2(lk)
                    except Exception as e:
                        clog(e)
                        try:
                            d = getContentWget(lk)
                        except Exception as e:
                            clog(e)                            
                            time.sleep(60)
                            try:
                                d = fetch2(lk)
                            except Exception as e:
                                time.sleep(60)
                                clog(e)
                                try:
                                    d = getContentWget(lk)
                                except Exception as e:
                                    clog(e)
                if "status" not in d:
                    return ll                
                if d["status"]!=200 and d["status"]!=301 and d["status"]!=302 or len(d["data"].strip())==0:
                    d = getContentWget(lk)
                gawkersites = ["http://gawker.com",
                               "http://gizmodo.com",
                               "http://kotaku.com",
                               "http://jalopnik.com",
                               "http://lifehacker.com",
                               "http://deadspin.com",
                               "http://jezebel.com",
                               "http://io9.com",
                               "http://fleshbot.com",
                               "http://gawker.tv",
                               "http://cityfile.com",
                               "http://sploid.com",
                               "http://www.gawker.com",
                               "http://www.gizmodo.com",
                               "http://www.kotaku.com",
                               "http://www.jalopnik.com",
                               "http://www.lifehacker.com",
                               "http://www.deadspin.com",
                               "http://www.jezebel.com",
                               "http://www.io9.com",
                               "http://www.fleshbot.com",
                               "http://www.gawker.tv",
                               "http://www.cityfile.com",
                               "http://www.sploid.com"]
                s, h = returnTopDomainAndHost(d["url"])
                for gs in gawkersites:
                    if "http://"+s in gs:
                        lk = d["url"] = d["url"].replace("http://", "http://m.").replace("#!", "")
                        d = fetch2(lk)
                cnt = 0
                d["data"]=toUTF8(d["data"])
                if "url" in d:                
                    d["image"]=isImage(d["url"])                
                if "status" in d:                    
                    if d["status"]==200 \
                    or d["status"]==301 \
                    or d["status"]==302 \
                    and "cli.gs" not in d["url"] \
                    and ".pdf" not in d["url"] \
                    and ".js" not in d["url"] \
                    and ".mp3" not in d["url"] \
                    and ".doc" not in d["url"] \
                    and "www.facebook.com/login.php" not in d["url"] \
                    and "techmeme.com" not in d["url"]:                    
                        clog("findLinks adding: "+str(d['url']))
                        ll.append(d)                
                # special case for mc-affee urlshortener
                if "url" in d:                                
                    if "http://mcaf.ee/" in d["url"]:
                        for frame in BeautifulSoup(d["data"], parseOnlyThese=SoupStrainer("frame")):
                            if "src" in frame:
                                src = frame["src"]
                                if "http" in src:
                                    d = fetch(src)
                                    cnt = 0
                                    if "status" in d:
                                        while d["status"]!=200:
                                            cnt = cnt + 1
                                            if cnt>10:
                                                break
                                            d = fetch(d["url"])
                                            if "status" not in d:
                                                break
                                        d["data"]=toUTF8(d["data"])
                                        d["image"]=isImage(d["url"])
                                        ll = []
                                        ll.append(d)
        except Exception as e:
            clog(lk)
            traceback.print_exc(file=sys.stdout)
            content = {}
            content["url"] = lk
            content["status"] = 200
            content["data"] = "<div id='nr_error'>findlinks:"+str(e)+"</div>"
            content["image"] = False
            print(content)
            return [content]
    return ll

def getContentRuby(url, t1_name, t2_name, difficult=False):
    difficultsites = ['geenstijl']
    script = "/home/rabshakeh/Newsrivr/daemons/rubyreadability.rb"
    for u in difficultsites:
        if u in str(url).lower():
            script = "/home/rabshakeh/Newsrivr/daemons/rubyyreadability.rb"
    if difficult:
        script = "/home/rabshakeh/Newsrivr/daemons/rubyyreadability.rb"
    cmd = ["/usr/bin/ruby", script, t1_name, t2_name ]    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    error = p.stderr.read()
    if len(error)!=0:
        print(url)
        print(error)
    s = p.stdout.read()
    s = s.strip()
    if len(s)>0:
        print(s)
    
def getfilenames(content):
    t1 = NamedTemporaryFile(delete=False)
    t2 = NamedTemporaryFile(delete=False)
    """        
    m = hashlib.md5()
    spid=str(os.getpid())+str(time.time())
    m.update(spid)
    fnmd5 = m.hexdigest()    
    t1 = open("in-"+fnmd5+".txt", "w")
    t2 = open("out-"+fnmd5+".txt", "w")
    """
    t1.write(content)
    t1_name = t1.name
    t2_name = t2.name
    return t1_name, t2_name

def getLinkDensityPara(html):
    def _text(node):
        return " ".join(node.findAll(text=True))    
    elem = BeautifulSoup(html)
    link_length = len("".join([i.text or "" for i in elem.findAll("a")]))
    text_length = len(_text(elem))
    return old_div(float(link_length), max(text_length, 1))

def getContentDiv(s):
    try:
        super_positive_str = "(post_body[A-Z,a-z,0-9,-,_ ]*)|"
        super_positive_str += "(instapaper_body[A-Z,a-z,0-9,-,_ ]*)|"
        super_positive_str += "(entry_body_text[A-Z,a-z,0-9,-,_ ]*)|"        
        super_positive_str += "(article[A-Z,a-z,0-9,-,_ ]*)"
        SUPERPOSITIVE = re.compile(super_positive_str)
        soup = BeautifulSoup(s)
        whitespace = True
        for tag in soup.findAll("div"):
            if "id" in tag:
                if SUPERPOSITIVE.match(tag["id"].lower()):
                    #print getLinkDensityPara(str(tag))
                    if len(striptags(str(tag)))>300:
                        return str(tag)
            if "class" in tag:
                if SUPERPOSITIVE.match(tag["class"].lower()):
                    if len(striptags(str(tag)))>300:
                        return str(tag)
        return s
    except Exception as e:
        clog(e)
        return s
    
def removeForms(s):
    try:
        soup = BeautifulSoup(s)
        for tag in soup.findAll("form"):
            tag.extract()
        for tag in soup.findAll("select"):
            tag.extract()
        return str(soup).strip()
    except Exception as e:
        clog(e)
        return s    
    
def grabTheContent(content, link, data, raw=False):
    if len(data.strip())==0:
        return "no content available", "no content available"
    content2=content
    link2=link
    data2=data
    if not raw:
        data = removeForms(data)        
        data = getContentDiv(data)
    if "tweetdeck.com/twitter" in link and not raw:
        soup = BeautifulSoup(data)
        whitespace = True
        for tag in soup.findAll("div"):
            if "id" in tag:
                if "deckly-post"==tag["id"]:
                   data = str(tag)
    if "slashdot" in link:
        for i in range(0,20):
            f = feedparser.parse("http://rss.slashdot.org/Slashdot/slashdot")
            if "entries" in f:
                for i in f["entries"]:
                    if "title" in i:
                        if Levenshtein.ratio(content, str(i["title"]))>0.5:
                            if "summary" in i:
                                c = i["summary"]
                                c = c.replace("a href", "a target='blank' href")
                                return c, c
                        else:
                            time.sleep(30)
    if "scripting.com" in link:
        f = feedparser.parse("http://scripting.com/rss.xml")
        if "entries" in f:
            for i in f["entries"]:
                if "title" in i:
                    if Levenshtein.ratio(content, str(i["title"]))>0.5:
                        if "summary" in i:
                            c = i["summary"]
                            c = c.replace("a href", "a target='blank' href")
                            return text2simpleHtml(c), text2simpleHtml(grabContent(link, c))
    
    t1, t2 = getfilenames(data)
    getContentRuby(link, t1, t2, raw)
    content = open(t2, "r").read()
    os.remove(t1)
    os.remove(t2)    
    sanicontent = grabContent(link, content)
    if len(striptags(sanicontent).replace(" ", "").replace("\n", ""))<50 and not raw:        
        content, sanicontent = grabTheContent(content2, link2, data2, True)
        #time.sleep(60)        
    if getLinkDensityPara(content)>0.3:
        clog("getLinkDensityPara: CONTENT TOO MANY LINKS !!!")
        content = ""
    if getLinkDensityPara(sanicontent)>0.43:
        clog("SANICONTENT TOO MANY LINKS !!!")
        sanicontent = ""
    return content, sanicontent

def processHistogram(h):
    return old_div(float(len(set(h))),float(len(h)))     
    
class getWidthHeightImage(threading.Thread):
    def __init__ (self,img):
        threading.Thread.__init__(self)
        self.img = img
        self.size = (0,0)
        self.data = False
        self.format = ""
        self.validhistogram = True
        self.histogram_md5 = ''
        self.animated = True
    def run(self):
        ll = linkList(self.img)
        if len(ll)==0:
            return self.size
        self.img = ll[0]
        try:
            try:
                file = urllib.request.urlopen(self.img)
                fdata = file.read()
                im = cStringIO.StringIO(fdata) # constructs a StringIO holding the image
                i = Image.open(im)            
                self.size = i.size
                self.format = i.format
                if fdata:
                    self.data = base64.encodestring(fdata)
            except Exception as e:
                clog(self.img+": "+str(e))
                c = fetch(self.img)
                fdata = cStringIO.StringIO(c["data"])
                i = Image.open(fdata)                
                self.size = i.size
                self.format = i.format
                if c["data"]:
                    self.data = base64.encodestring(c["data"])            
            try:
                i.seek(1)
            except EOFError:
                self.animated = False
                i.seek(0)
            m = hashlib.md5()
            m.update(str(self.data))
            self.histogram_md5 = m.hexdigest()            
            if processHistogram(i.histogram())<0.01:
                self.validhistogram = False
            #print
            #print self.img
            #print processHistogram(i.histogram())
            #print "----------------"
        except Exception as e:
            clog(self.img+": "+str(e))

def returnTopDomainAndHost(url):
    x = urlparse.urlsplit(url)
    x = (x.netloc).split(".")
    dn = []
    h = ""
    if len(x)>0:
        h = x[0]
    for i in range(0, len(x)):
        if i>len(x)-3:
            dn.append(x[i])
    s = ""
    for i in range(0, len(dn)):
        s += dn[i]
        if i<len(dn)-1:
            s += "."
    return s, h

def checkURL(url):
    try:
        if "leeg." in url or "empty." in url or "spacer." in url or "trans." in url:
            return False
        h = urllib.request.urlopen(url).headers.headers
        return True
    except Exception as e:
        clog("checkUrl:"+str(url)+" "+str(e))
        return False
    
def imageAlreadySeen(tweet_id_str, histogram_md5):
    return False
    if getCollImageMd5s().find({"tweet_id_str":tweet_id_str, "histogram_md5":histogram_md5}).count()>0:
        return True
    return False

    
def youtubeAlreadySeen(tweet_id_str, videotag):
    return False
    if getCollYoutubeTags().find({"tweet_id_str":tweet_id_str, "videotag":videotag}).count()>0:
        return True
    return False

def findBiggestImages(url, html, tweet_id_str, id_str):
    domain, host = returnTopDomainAndHost(url)
    if len(domain)==0:
        return 
    soup = BeautifulSoup(html)
    imgs = soup.findAll("img");
    biggest = {"size":0,"src":"", "width":0, "height":0, "notbase64":True, "validhistogram":False, "histogram_md5":""}
    #return biggest, 0
    tq = []
    whl = []
    cnt = 0
    ads = cPickle.load(open("/home/rabshakeh/Newsrivr/daemons/adservers.pickle", "r"))    
    for i in imgs:
        if "src" in i:
            td, host = returnTopDomainAndHost(i["src"])
            if td in ads or "/adx/" in i["src"] \
            or "adx_" in i["src"] \
            or "/ad/" in i["src"] \
            or "/ads/" in i["src"] \
            or "ad" in host \
            or "banner" in i["src"] \
            or "captcha" in i["src"] \
            or "P1130541.JPG.jpeg" in i["src"] \
            or "navPackedSprites" in i["src"] \
            or "logo" in i["src"] \
            or "blogbooks.jpg" in i["src"] \
            or "sargasso_logo.png" in i["src"] \
            or ("logo" in i["src"] and ".gif" in i["src"]):
                pass
            else:
                if "src" in i:
                    if len(i["src"])>0:
                        if i["src"][0]!="/" and i["src"][0].lower()!="h":
                            i["src"] = "../"+i["src"]
                    if checkURL(urlparse.urljoin(url, i["src"])):
                        if cnt<300:
                            t = getWidthHeightImage(urlparse.urljoin(url, i["src"]))
                            t.start()
                            tq.append(t)
                        cnt += 1            
    for t in tq:
        t.join()
        if t.data and not t.animated:
            whl.append((t.size, t.img, t.format, t.data, t.validhistogram, t.histogram_md5))
    num_big_images = 0
    for wh in whl:
        whs = wh[0][0]*wh[0][1]
        if whs>300000:
            num_big_images += 1        
        if whs>biggest["size"] and wh[4] and not imageAlreadySeen(tweet_id_str, wh[5]):
            if whs>5000:# or "media.nu.nl" in wh[1] and "http" in wh[1].lower():
                biggest["size"]=whs
                biggest["src"]=wh[1]
                biggest["width"]=wh[0][0]
                biggest["validhistogram"] = wh[4]
                biggest["histogram_md5"] = wh[5]
                if biggest["width"]>706:
                    biggest["width"]=706
                biggest["extrabreaks"]=False
                if biggest["width"]>550:
                    biggest["extrabreaks"]=True
                    biggest["width"]=706
                biggest["height"]=wh[0][1]
                try:
                    im = cStringIO.StringIO(base64.decodestring(wh[3]))
                    i = Image.open(im)
                    nh = float(i.size[1]) / float(i.size[0]) * 80
                    i = i.resize((80, int(nh)),Image.ANTIALIAS)
                    outdata = cStringIO.StringIO()
                    bts = biggest["src"].split(".")
                    format = bts[len(bts)-1].lower()            
                    if format=="jpg":
                        format = "jpeg"
                    if format!="jpeg" and format!="png" and format!="gif":
                        pass
                    else:
                        i.save(outdata, format)                    
                        biggest["thumbnail"] = "data:image/jpeg;base64,"+base64.encodestring(outdata.getvalue())
                except Exception as e:
                    clog("thumbnail:"+str(e))
                #if "twitpic" in biggest["src"] or "media.egotastic.com" in biggest["src"] or "plixi" in html.lower():
                biggest["format"]=wh[2].lower()
                biggest["data"]=""# (niet nodig nu) wh[3]
                if "twitpic" in biggest["src"] or "media.egotastic.com" in biggest["src"] or "plixi" in html.lower():
                    biggest["srcbase64"]="data:image/"+biggest["format"]+";base64,"+wh[3]
                    biggest["src"]=biggest["srcbase64"]
                biggest["notbase64"]=False
                drops = getCollImageMd5s()
                if drops.count()==0:
                    drops.create_index([("tweet_id_str",DESCENDING), ("histogram_md5",DESCENDING)], unique=True);
                try:
                    getCollImageMd5s().insert ({'id_str':id_str, 'tweet_id_str':tweet_id_str, 'histogram_md5':biggest["histogram_md5"]}, safe=True)
                except Exception as e:
                    clog("findBiggestImages: "+str(e))
    return biggest, num_big_images

def joinWordList(l):
    s=""
    for w in l:
        if w!="":
            s+=w.strip()+" "
    return s

def striptags(data):
    soup = BeautifulSoup(data)
    for tag in soup.findAll(True):
        tag.hidden = True
    data = soup.renderContents()
    soup = BeautifulSoup(data)
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    html = soup.renderContents()    
    for i in range(0, 3):
        html = html.replace("  ", " ")    
    return html 

class SafeData(object):
    pass

class Promise(object):
    """
    This is just a base class for the proxy class created in
    the closure of the lazy function. It can be used to recognize
    promises in code.
    """
    pass

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (type(None), int)):
        return s
    if isinstance(s, Promise):
        return str(s).encode(encoding, errors)
    elif not isinstance(s, str):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return str(s).encode(encoding, errors)
    elif isinstance(s, str):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s
    
def urlquote(url, safe='/'):
    """
    A version of Python's urllib.quote() function that can operate on unicode
    strings. The url is first UTF-8 encoded before quoting. The returned string
    can safely be used as part of an argument to a subsequent iri_to_uri() call
    without double-quoting occurring.
    """
    return toUTF8(urllib.parse.quote(smart_str(url), safe))
    
def urlize(text, trim_url_limit=None, nofollow=False, autoescape=False):
    """
    Converts any URLs in text into clickable links.

    Works on http://, https://, www. links and links ending in .org, .net or
    .com. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right
    thing.

    If trim_url_limit is not None, the URLs in link text longer than this limit
    will truncated to trim_url_limit-3 characters and appended with an elipsis.

    If nofollow is True, the URLs in link text will get a rel="nofollow"
    attribute.

    If autoescape is True, the link text and URLs will get autoescaped.
    """
    DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']    
    LEADING_PUNCTUATION  = ['(', '<', '&lt;']
    TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']
    unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
    word_split_re = re.compile(r'(\s+)')
    punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
    simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
    link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
    html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
    hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
    trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (len(x) > limit and ('%s...' % x[:max(0, limit - 3)])) or x
    safe_input = isinstance(text, SafeData)
    words = word_split_re.split(toUTF8(text))
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = None
        if '.' in word or '@' in word or ':' in word:
            match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            # Make URL we want to point to.
            url = None
            if middle.startswith('http://') or middle.startswith('https://'):
                url = urlquote(middle, safe='/&=:;#?+*')
            elif middle.startswith('www.') or ('@' not in middle and \
                    middle and middle[0] in string.ascii_letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                url = urlquote('http://%s' % middle, safe='/&=:;#?+*')
            elif '@' in middle and not ':' in middle and simple_email_re.match(middle):
                url = 'mailto:%s' % middle
                nofollow_attr = ''
            # Make link.
            if url:
                trimmed = trim_url(middle)
                if autoescape and not safe_input:
                    lead, trail = escape(lead), escape(trail)
                    url, trimmed = escape(url), escape(trimmed)
                middle = '<a target="_blank" href="%s"%s>%s</a>' % (url, nofollow_attr, trimmed)
                words[i] = str('%s%s%s' % (lead, middle, trail))
            else:
                if safe_input:
                    words[i] = str(word)
                elif autoescape:
                    words[i] = escape(word)
        elif safe_input:
            words[i] = str(word)
        elif autoescape:
            words[i] = escape(word)
    return u''.join(words)
    
def parseHashUser(text):
    # parse @tweeter
    text = re.sub(
        r'(?<![a-zA-Z-_])@([\w\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff]+)',
        lambda x: "<a target='_blank' href='http://newsrivr.com/%s'>%s</a>"\
             % (x.group()[1:].strip().replace("@", ""), x.group().strip()),
        text)
    
    # parse #hashtag
    text = re.sub(
        r' #([\w\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff]+)',
        lambda x: " <a target='_blank' href='http://twitter.com/search?q=%%23%s'>%s</a>"\
             % (x.group()[1:], x.group()),
        text)

    # parse #hashtag
    text = re.sub(
        r'^#([a-zA-Z0-9_-]+)',
        lambda x: "<a target='_blank' href='http://twitter.com/search?q=%%23%s'>%s</a>"\
             % (x.group()[1:], x.group()),
        text)
    
    return text
    
def youtubeVideoTagFromUrl(url):
    url = str(url)    
    if "www.youtube.com/watch?v=" not in url:
        return None
    videotag = url.split("=")
    if videotag>1:
        videotag=videotag[1]
        return videotag
    else:
        return None       

def youtubeVideoTagFromUrl2(url):
    url = str(url)
    if "youtube.com" in url:
        url = url.split("/")
        if len(url)>0:
            videotag = url[len(url)-1]
            m = re.search('v\=([a-zA-Z0-9-_=]+)', videotag)
            if m:
                vs = m.group(0).split("=")
                if len(vs)>1:
                    videotag=vs[1]
                    return videotag
    return None

def youtubeVideoTagFromUrl3(url):
    url = str(url)
    if "youtube.com" in url:
        url = url.split("/")
        if len(url)>0:
            videotag = url[len(url)-1]
            vs = videotag.split("?")
            if len(vs)>1:
                return vs[0]
    return None

def youtubeVideoFromJS(data):
    data2 = data.split("playnav.setVideoId(")
    if len(data2)>1:
        data3 = data2[1].split(")")
    else:
        return None
    if len(data3)>0:
        return data3[0].replace("'", "").replace('"', '')
    else:
        return None

def youtubeVideoTagFromHTMLParam2(data):
    '<param name="movie" value="http://www.youtube.com/e/gkwrYiP6dck">'
    for param in BeautifulSoup(data, parseOnlyThese=SoupStrainer("param")):
        if "value" in param:
            value = param["value"]
            if "youtube" in value:
                value = value.split("e/")
                if len(value)>1:
                    value = value[1].split("?")
                    value = value[0]
                    return value  
    return None

def youtubeVideoTagFromHTMLParam(data):
    "http://www.youtube.com/v/-8MvWg-wCtE?fs=1&hl=en_US"
    for param in BeautifulSoup(data, parseOnlyThese=SoupStrainer("param")):
        if "value" in param:
            value = param["value"]
            if "youtube" in value:
                value = value.split("v/")
                if len(value)>1:
                    value = value[1].split("?")
                    value = value[0]
                    return value  
    return None

def youtubeTagFromIframe(data):
    '<p><iframe src="http://www.youtube.com/embed/GATIYgOKp_8" width="560" height="345" frameborder="0"></iframe></p>'
    for iframe in BeautifulSoup(data, parseOnlyThese=SoupStrainer("iframe")):
        if "src" in iframe:
            if "youtube.com/embed/" in iframe["src"]:
                s = iframe["src"].split("embed/")
                if len(s)>0:
                    return s[1]

def youtubeTagFromObject(data):
    '<p><object height="269" width="425"><embed src="http://www.youtube.com/v/6W07bFa4TzM?fs=1&amp;hl=en_US" type="application/x-shockwave-flash" allowscriptaccess="always" height="269" width="425"></object></p>'
    for embed in BeautifulSoup(data, parseOnlyThese=SoupStrainer("embed")):
        if "src" in embed:
            return youtubeVideoTagFromUrl3(embed["src"])

def youtubeTagFromObject2(data):
    '<object type="application/x-shockwave-flash" data="http://www.youtube.com/v/fMW3W-G43gI&amp;amp;rel=1&amp;amp;fs=1&amp;amp;showsearch=0" width="480" height="296" id="vvq4d651c03215ab" style="visibility: visible; "><param name="wmode" value="opaque"><param name="allowfullscreen" value="true"></object>'
    for obj in BeautifulSoup(data).findAll(True):
        value = str(obj)
        if "youtube" in value:            
            value = value.split("youtube.com")
            if len(value)>1:
                m = re.search('v\=([a-zA-Z0-9-_=]+)', value[1])
                if m:
                    vs = m.group(0).split("=")
                    if len(vs)>1:
                        videotag=vs[1]
                        return videotag
                value = value[1].split("v/")
                if len(value)>1:
                    splitter = "/"
                    for c in value[1]:
                        if c=='?':
                            splitter = "?"
                            break
                        if c=='&':
                            splitter = "&"
                            break
                    value = value[1].split(splitter)
                    value = value[0]
                    return value  

def youtubeFromJSON(data):
    try:
        def newVideoPlayer(x):
            return x
        for sc in BeautifulSoup(data, parseOnlyThese=SoupStrainer("script")):
            if "newVideoPlayer" in str(sc):
                if len(sc.contents[0])>0:
                    null = None
                    false = False
                    true = True
                    data = eval(sc.contents[0].strip().replace(" ", "").replace(";", ""))
                    ds = data["player"].split("&")
                    if len(ds)>0:
                        ds = ds[0].split("/")
                        if len(ds)>0:
                            return ds[len(ds)-1]
    except Exception as e:
        clog(e)
        return None
    
def YoutubeCallback(jsondata):
    desc = ""
    if "entry" in jsondata:
        if "media$group" in jsondata["entry"]:
            if "media$description" in jsondata["entry"]["media$group"]:
                desc = jsondata["entry"]["media$group"]["media$description"]["$t"]
    thumbs = []
    if "entry" in jsondata:
        if "media$group" in jsondata["entry"]:
            if "media$thumbnail" in jsondata["entry"]["media$group"]:    
                for i in jsondata["entry"]["media$group"]["media$thumbnail"]:
                    if "'width': 120" in str(i):
                        thumbs.append({"src":i["url"]})
    return thumbs, desc

def parseYoutube(url, data, tweet_id_str, id_str):
    if "youtu.be" in url:
        surl = url.split("/")
        videotag = surl[len(surl)-1]
    elif "youtube" not in data.lower():
        return None
    
    videotag = youtubeVideoTagFromUrl(url)
    if not videotag:
        videotag = youtubeFromJSON(data)
    if not videotag:
        videotag = youtubeVideoTagFromHTMLParam(data)
    if not videotag:
        videotag = youtubeVideoTagFromHTMLParam2(data)        
    if not videotag:
        videotag = youtubeTagFromObject(data)                
    if not videotag:
        videotag = youtubeVideoFromJS(data)        
    if not videotag:
        videotag = youtubeVideoTagFromUrl2(url)
    if not videotag:
        videotag = youtubeVideoTagFromUrl3(url)        
    if not videotag:
        videotag = youtubeTagFromIframe(data)
    if not videotag:
        videotag = youtubeTagFromObject2(data)
    if not videotag:        
        return None

    videotag = videotag.split("&")[0]
    
    if youtubeAlreadySeen(tweet_id_str, videotag):
        return None
    
    jsonurl = "http://gdata.youtube.com/feeds/api/videos/"+videotag+"?v=2&alt=json-in-script&callback=YoutubeCallback"
    jsondata = urllib.request.urlopen(jsonurl).read();

    if "errors" in str(jsondata) or "414 Request-URI Too Large" in str(jsondata):
        return None

    getCollYoutubeTags().insert ({'id_str':id_str, 'tweet_id_str':tweet_id_str, 'videotag':videotag}, safe=True)
    
    thumbs = []
    if jsondata.strip().startswith("YoutubeCallback("):
        exec("thumbs="+jsondata)
    
    data = {}
    if len(thumbs)==0:
        return data
    data["videotag"]=videotag
    if thumbs:
        data["thumbs"]=thumbs[0]
        data["desc"]=parseHashUser(urlize(parseHashUser(thumbs[1].replace("\n", ""))))
        if len(striptags(data["desc"]).strip())!=0:
            data["desc"] += "<div class=\"clear\"><!-- --></div>"
    return data
        
def parseTed(url, data):
    if "ted.com" in url.strip().lower():
        for input in BeautifulSoup(data, parseOnlyThese=SoupStrainer("input")):
            if "class" in input:
                if input["class"]=="copy_paste":
                    if "value" in input:
                        return input["value"]
    return None

def parseVimeo(data):
    '<link rel="alternate" href="http://vimeo.com/api/oembed.json?url=http://vimeo.com/19231255" type="application/json+oembed" />'
    for link in BeautifulSoup(data, parseOnlyThese=SoupStrainer("link")):
        if "json" in str(link):
            if "href" in link:
                data = fetch(link['href'])
                if "data" in data:
                    jd = simplejson.loads(data["data"])
                    for iframe in BeautifulSoup(jd["html"], parseOnlyThese=SoupStrainer("iframe")):
                        if "src" in iframe:
                            jd["iframe"] = iframe["src"]
                            try:
                                jd["desc"] = urlize(jd["description"])
                            except:
                                jd["desc"] = urlize(toUTF8(jd["description"])) 
                            if len(striptags(jd["desc"]).strip())!=0:
                                jd["desc"] += "<div class=\"clear\"><!-- --></div>"                            
                    return jd
    return None
     
def getVimeoClipId(s):
    try:
        if "vimeo.com" in s and "clip_id" in s:
            soup = BeautifulSoup(s)
            for obj in soup.findAll("object"):
                for param in obj.findAll("param"):
                    if "name" in param:
                        if param["name"]=="src":
                            if "value" in param:
                                s=param["value"].split("clip_id=")
                                if len(s)>1:
                                    clipid = s[1].split("&")[0].strip()                                    
                                    return clipid
        return ""
    except Exception as e:
        clog(e)
        return ""

def parseSlideShare(url):
    try:
        from BeautifulSoup import BeautifulStoneSoup
        r = fetch2("http://www.slideshare.net/api/oembed/1?url="+url+"&format=json")
        data = simplejson.loads(r["data"])
        data["html"] = data["html"].replace("355", "590").replace("425", "706")
        x= str(BeautifulStoneSoup(data["html"], convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0])        
        x = x.replace("embed name=", "embed wmode='transparent' name=")
        x = x.replace('<param name="allowFullScreen" value="true">', '<param name="allowFullScreen" value="true"></param><param name="wmode" value="transparent"></param>')
        return x
    except Exception as e:
        return "Couldn't fetch slideshare:"+str(url)+"<hr>"+str(e)
   
def parseCinch(url, data):
    try:
        from BeautifulSoup import BeautifulStoneSoup
        for a in BeautifulSoup(data, parseOnlyThese=SoupStrainer("a")):
            if "href" in a:
                if "mp3" in a["href"]:
                    return {'mp3':urlparse.urljoin(url, a["href"])}
    except Exception as e:
        clog("Couldn't parse cinch"+str(e))
        return None
    
def retMentions(text):
    l = []
    text = re.sub(r'(?<![a-zA-Z-_])@([a-zA-Z0-9_-]+)', lambda x: l.append(x.group().strip()), text)
    return l

def procesContentToNewsRivrDrop(content, id_str, screen_name, userid, tweet_id_str):
    processed_content = {}
    content = content.replace("http", " http").replace("  http", " http")
    content = toUTF8(striptags(content))
    #open("/home/rabshakeh/Newsrivr/daemons/pids/"+str(os.getpid())+".txt", "w").write(content)
    processed_content["org_content"]=parseHashUser(urlize(content, nofollow=True))
    #implement this: @([A-Za-z0-9_]+)
    processed_content["followed_links"]=[]
    processed_content["images"]=[]
    processed_content["mentions"] = retMentions(content)
    m = hashlib.md5()
    m2 = hashlib.md5()    
    l =  findLinks(content.replace("\n", " "))
    if len(l)==0 and len(linkList(content.replace("\n", " ")))!=0:
        time.sleep(1)
        l =  findLinks(content.replace("\n", " "))
    numlinks = len(l)
    
    for i in l:
        if not i["image"]:            
            if "data" in i:
                data, sanatized_data = grabTheContent(content, i["url"], i["data"])
                if str(data).count("/")>250:
                    data = sanatized_data = ""
                if str(data).count("{")>150:
                    data = sanatized_data = ""                                        
                followed_link = {}
                if numlinks>0 and i!=l[numlinks-1]:
                    followed_link["adddivider"] = True
                youtube = parseYoutube(i["url"], i["data"], tweet_id_str, id_str)
                ted = parseTed(i["url"], i["data"])
                cinch = False
                if "cinchcast.com" in i["url"]:                    
                    cinch = parseCinch(i["url"], i["data"])
                vimeo = None
                if "vimeo.com" in i["data"] and "clip_id" in i["data"]:
                    id = getVimeoClipId(data)
                    if len(id)!=0:
                        vimeojsonlink = '<link rel="alternate" href="http://vimeo.com/api/oembed.json?url=http://vimeo.com/'+id+'" type="application/json+oembed" />'
                        vimeo = parseVimeo(vimeojsonlink)
                if "vimeo" in i["url"] and not vimeo:
                    vimeo = parseVimeo(i["data"])
                if ".slideshare.net" in i["url"]:
                    followed_link["simplehtml"] = parseSlideShare(i["url"])
                if ".slideshare.net" not in i["url"] \
                and "youtube.com/" not in i["url"] \
                and ("http://blog.ted.com" not in i["url"] \
                    or "http://ted.com" not in i["url"] \
                    or "http://www.ted.com" not in i["url"]) \
                and "vimeo.com" not in i["url"]:
                    followed_link["simplehtml"] = sanatized_data
                    followed_link["simplehtml"] = followed_link["simplehtml"].replace("\n", "").replace("\\n", "")
                    if len(striptags(followed_link["simplehtml"]).replace(" ", "").replace("\n", ""))<50 and "nr_error" not in followed_link["simplehtml"]:
                        followed_link["simplehtml"]=""                        
                    #followed_link["simplehtmllen"]=len(striptags(followed_link["simplehtml"]).replace(" ", "").replace("\n", ""))
                    sourcemd5 = content+screen_name             
                    if sourcemd5.strip()=="":
                        sourcemd5 = striptags(followed_link["simplehtml"])
                    if sourcemd5.strip()=="":
                        sourcemd5 = id_str
                    m.update(sourcemd5)
                    processed_content["md5"]=m.hexdigest()                    
                    if len(followed_link["simplehtml"])!=0:
                        m2.update(followed_link["simplehtml"])
                        processed_content["htmlmd5"]=m2.hexdigest()
                    else:
                        processed_content["htmlmd5"]=processed_content["md5"]
                    if "url" in i:
                        photosites = ["twitrpix", "icanhascheezburger", "flickr", "twitpic", "yfrog", "instagr.am", "mobypicture", "picplz.com", "plixi"]
                        td, host = returnTopDomainAndHost(i["url"])
                        #print td, host, len(followed_link["simplehtml"])
                        for ps in photosites:
                            if ps in td.lower() or ps in host.lower():
                                if len(striptags(followed_link["simplehtml"]))<3000:
                                    followed_link["simplehtml"]=""
                        specials = ["yfrog"]
                        useallhtml = False
                        photosites.remove("plixi")
                        for u in photosites:
                            if u in i["url"].lower():
                                useallhtml = True
                        if useallhtml:
                            biggestimage, num_big_images = findBiggestImages(i["url"], i["data"], tweet_id_str, id_str)
                        else:                        
                            biggestimage, num_big_images = findBiggestImages(i["url"], data, tweet_id_str, id_str)
                        if biggestimage["size"]==0:            
                            biggestimage, num_big_images = findBiggestImages(i["url"], i["data"], tweet_id_str, id_str)
                        if biggestimage["size"]>0:
                            if biggestimage["size"]<50000 and len(striptags(followed_link["simplehtml"]))<20:
                                #niet toevoegen
                                pass
                            else:
                                if "slashdot" not in i["url"]:
                                    followed_link["image"]=biggestimage
                                    if num_big_images>6:
                                        followed_link["simplehtml"]= "Found "+str(num_big_images) + " other large images<br/><br/>"
                        usplit = urlparse.urlsplit(i['url'])
                        if len(usplit.path)<1:
                            followed_link["simplehtml"] = ""#"<a target='_blank' href='"+i["url"]+"'>"+i["url"]+"</a><br/>NewsRivr was intended for use on individual articles and not home pages."
                if cinch:
                    followed_link["cinch"]=cinch
                if vimeo:
                    followed_link["vimeo"]=vimeo
                    m.update(vimeo["html"]+content+screen_name)
                    processed_content["md5"]=m.hexdigest()
                    processed_content["htmlmd5"]=processed_content["md5"]                    
                if youtube:
                    followed_link["youtube"]=youtube
                    m.update(youtube["videotag"]+content+screen_name)
                    processed_content["md5"]=m.hexdigest()
                    processed_content["htmlmd5"]=processed_content["md5"]
                if ted:
                    m.update(ted)
                    processed_content["md5"]=m.hexdigest()
                    processed_content["htmlmd5"]=processed_content["md5"]
                    followed_link["simplehtml"]=ted
                followed_link["link"]=i
                if "adddivider" in followed_link:
                    if "simplehtml" in followed_link:
                        if len(followed_link["simplehtml"].strip())==0:
                            del followed_link["adddivider"]
                if "http://twitter.com/#!/" in i["url"]:
                    followed_link["simplehtml"] = "twitter links ignored"
                if ".wikipedia.org" in i["url"]:
                    followed_link["simplehtml"] = "wikipedia links ignored"
                processed_content["followed_links"].append(followed_link)
        else:
            t = getWidthHeightImage(i["url"])
            t.run()
            imgdir = {}
            imgdir["size"]=t.size
            imgdir["src"]=i["url"]
            imgdir["width"]=t.size[0]
            imgdir["validhistogram"] = t.validhistogram
            imgdir["histogram_md5"] = t.histogram_md5
            if imgdir["width"]>706:
                imgdir["width"]=706
            if imgdir["width"]>550:
                imgdir["extrabreaks"]=True
                imgdir["width"]=706
            if not t.animated:
                processed_content["images"].append(imgdir)
    if "md5" not in processed_content:
        m.update(content+screen_name)
        processed_content["md5"]=m.hexdigest()
        processed_content["htmlmd5"]=processed_content["md5"]
    if len(processed_content["images"])>0:
        processed_content["can_be_opened"] = True
    else:
        processed_content["can_be_opened"] = False
        for l in processed_content["followed_links"]:
            if "simplehtml" in l:
                if len(l["simplehtml"].strip())!=0:
                    processed_content["can_be_opened"] = True
            if "image" in l:
                if len(l["image"]["src"])!=0:
                    processed_content["can_be_opened"] = True
            if "youtube" in l:
                processed_content["can_be_opened"] = True
            if "vimeo" in l:
                processed_content["can_be_opened"] = True                
            if "cinch" in l:
                processed_content["can_be_opened"] = True                
    lcnt = 0
    for l in processed_content["followed_links"]:
        if "data" in l["link"]:
            del l["link"]["data"]
        html = ""
        shortened = False
        findclosetag = False
        wc = 0
        lcnt = lcnt + 1
        if "simplehtml" in l:
            if 1==2:#"<table" in l["simplehtml"]:
                html += "<div id='hide_"+id_str+"_"+str(lcnt)+"' style='display:none;'>"
                html += l["simplehtml"]
                shortened = True
            else:
                sourcehtml = l["simplehtml"]
                sourcehtml = sourcehtml.replace("<br />", "<br>")
                seperator = "</p>"
                if seperator not in sourcehtml:
                    seperator = "<br>"
                splithtml =sourcehtml.split(None)
                if len(splithtml)>100:
                    for i in splithtml:
                        html += i + " "
                        wc += 1
                        if wc>50 and not shortened and not findclosetag:
                            findclosetag = True                                
                        if findclosetag:
                            if seperator in i and (len(splithtml)-wc)>50 and not shortened:
                                shortened = True
                                findclosetag = False
                                html += "<div class='nr_contenthider' id='nr_hide_"+id_str+"_"+str(lcnt)+"' style='display:none;'>"
            if shortened:
                html += "</div><a id='nr_readmore_"+id_str+"_"+str(lcnt)+"' href='#' onclick='javascript:showContent(\""+id_str+"_"+str(lcnt)+ \
                "\"); return false;' style=\"float:right;\"><img src=\"http://esther.active8.nl/static/images/readmore.png\" alt=\"Read more\" border=\"0\" />Read more...</a>"
                l["simplehtml"] = html                                
    return processed_content

def base64ProfilePic(t, d):
    try:
        if "user" in t:
            if "profile_image_url" in t["user"]:
                bt = t["user"]["profile_image_url"].replace("_normal", "_reasonably_small")
                try:
                    data = urllib.request.urlopen(bt).read()
                    fdata = cStringIO.StringIO(data)
                    i = Image.open(fdata)
                except (Exception) as e:
                    print(e)
                    data = urllib.request.urlopen(d["user"]["profile_image_url"]).read()
                    fdata = cStringIO.StringIO(data)
                    i = Image.open(fdata)
                if old_div(float(i.size[1]), float(i.size[0]))>0.5:            
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
                return d
    except:
        traceback.print_exc(file=sys.stdout)
        
def getLinkDensityPara(html):
    def _text(node):
        return " ".join(node.findAll(text=True))    
    elem = BeautifulSoup(html)
    link_length = len("".join([i.text or "" for i in elem.findAll("a")]))
    text_length = len(_text(elem))
    return old_div(float(link_length), max(text_length, 1))

def main():
    #c = open("test.html", "r").read()
    #c = removeExtraBreaks(c)
    #open("test2.html", "w").write(c)
    #return
    #c = open("usedforscoring.html", "r").read()
    #youtube = parseYoutube("http://www.nrcnext.nl/blog/2011/02/23/e-t-is-terug/", c)
    #print youtube
    #data, sanatized_data = grabTheContent('x', 'x', c)
    #print sanatized_data
    #print getContentWget("http://nyti.ms/h0UiPS")
    #return

    os.system("clear")

    tweet = "China: Dragon or Drag? WATCH: http://t.co/AzLGgnj" # embedded movies not shown    
    tweet = "Watching NASA's livestream from space. Fascinating. http://ustre.am/rrom" # embed ustream
    tweet = "2011-03-21 19:29:55: https://www.facebook.com/video/video.php?v=10150169313551397&oid;=41794571093"
    tweet = "Pictures of Elizabeth Taylor and Michael Jackson. Might as well get used to this. http://r2.ly/r3wp"
    tweet = "The Manifesto Of Blonde Ambition! http://bit.ly/fVv9Ya RT" # geen youtube    
    tweet = "2. #in10blogt: What design can do http://bit.ly/hTxLR0" # vaag flash bonkje
    tweet = "Congrats aan m'n kleurspecialist @marrietgakes met haar nominatie voor coiffure award http://plixi.com/p/87550788" # plixi link werkt niet
    tweet = "11. Dit vind ik gewoon zo briljant: http://youtu.be/SgGfBiswon0" # geen filmpje
    tweet = "Iedere woensdag een stukje van mij over 'arbeidsmarkt' in nrcnext. Vorige week dit, http://www.mvcommunicatie.nl/l/en/library/download/13730" # encoded stuff
    tweet = "Men's Journal - How does a blind man mountain bike or navigate the wilderness alone? Here's how: http://su.pr/1qDHNR" # geen content
    tweet = "WC-Eend on steroids: Check deze tweet van PVV'er Van Doorn. Citeert zichzelf en zegt dan hij het met zichzelf eens is http://bit.ly/gndqJ1" # plaatjes negeren en text van tweet meenemen
    tweet = 'Apple developers...anyone gotten this "developer information update" in the iTunes connect store before? http://t.co/hIa74OZ'
    tweet = "@Teunvandekeuken http://www.youtube.com/watch?v=9StEAK8e9I4"
    tweet = "World of Psychology: Best of Our Blogs: May 27, 2011 http://bit.ly/miCyqy"
    tweet = "Hier de lezing ter afsluiting van mijn hoogleraarschap http://www.femkehalsema.nl/2011/05/27/politiek-in-de-jaren-nul/ #fhleonardo"

    tweet = "'Nederlandse komkommers onder verdenking': http://op.nu.nl/lWrjA4"
    tweet = "Opnieuw dode in Duitsland door darmbacterie: http://op.nu.nl/lH2kDF"

    tweet = "World of Psychology: 10 Steps to Conquer Perfectionism http://bit.ly/jhLHOW"
    tweet = "Vette waterhozen voor de Australische kust: Weet je wat ook tof was? De enorme waterhozen voor de kust van New So... http://cli.gs/NVB1K"
    tweet = "OK, iPod op een stok! http://t.co/5zJUsA3"
    tweet = "Peter Teffer: Wie op Facebook zit, wordt nog geen narcist - Trouw Opinie - http://t.co/Tg83YUB"
    #tweet = "Smullen. GroenLinks sloopt GroenLinks: Muhaaaa, we gaan weer GroenLinks bashen. Met dank aan het rechtsradicale tabl... http://t.co/c9SMlXg"
    #http://twitter.com/#!/AutoWeek/status/49417407135092736
    #tweet = open("utf8string.txt", "r").read()
    #open("utf8string2.txt", "w").write(tweet)
    
    drop = procesContentToNewsRivrDrop(tweet, "123", "test", "", '223480661')
    
    clog(drop)
    open("test.json", "w").write(str(drop))
    print()
    print()
    try:
        os.remove("test.html")
    except:
        clog("test.html not found to remove")
    
    ht = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>'
    ht += """
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.0/jquery.min.js"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.8/jquery-ui.min.js" type="text/javascript"></script>    
    <script>    
function showContent(id_str) {
    $("#nr_hide_" + id_str).show("blind", {
        percent: 100
    },
    500, null);
    $("#nr_readmore_" + id_str).hide("blind", {
        percent: 100
    },
    500, null);    
}</script>"""
    ht += '</head><body>'
    ht += drop["org_content"]
    ht += "<hr>"
    for i in drop["followed_links"]:
        try:
            ht += '<img src="'+i["image"]['thumbnail']+'"><br/><br/>\n'
            ht += '<img src="'+i["image"]['src']+'">\n'
        except:
            pass
        try:
            ht += 'YOUTUBE VIDEOTAG: <a href="http://www.youtube.com/watch?v='+i["youtube"]['videotag']+'">'+i["youtube"]['videotag']+"</a><br/>"
            ht += 'YOUTUBE desc: '+i["youtube"]['desc']
        except:
            pass
        try:
            ht += "<br/><b>vimeo link: "+str(i["vimeo"]["video_id"])+"</b><br/><br/>"
        except Exception as e:
            pass
        try:
            ht += i["simplehtml"]
        except Exception as e:
            clog("geen html gevonden"+str(e))
        if "adddivider" in i:
            ht += "<hr>"
    
    ht += "<hr></body></html>"
    open("test.html", "w").write(ht)
    os.system("open test.html")
        
if __name__=="__main__":
    main()

