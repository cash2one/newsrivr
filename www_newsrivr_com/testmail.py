from django.core.management import setup_environ
import pymongo

import settings
from datetime import datetime
setup_environ(settings)

import mailer
from pymongo import objectid
from django.template import loader, Context, Template
from BeautifulSoup import BeautifulSoup, Comment

def striptags(data):
    soup = BeautifulSoup(data)
    for tag in soup.findAll(True):
        tag.hidden = True
    data = soup.renderContents()
    soup = BeautifulSoup(data)
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]
    return soup.renderContents()

def getDB():
    conn = pymongo.Connection(settings.MONGOSERVER, settings.MONGOPORT)    
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

def getUserByMD5(md5):
    users = getCollUsers()
    sd = {"newsrivr_userid_md5": md5}
    return users.find_one(sd)
    
def mailDrop(_id, frommail, reply_to, tomail, mail_templates, errorstr, replyto_name="Bezoeker" ):
    data = None
    data = getCollDrops().find_one({"_id": objectid.ObjectId(_id)})    
    if not data:
        return
    
    user = getUserByMD5(data["newsrivr_userid_md5"])
    if not user:
        return
    
    if "name" in user:
        name = user["name"]
    else:
        name = user["screen_name"]

    subject = striptags(data["org_content"])
    
    #for key in cfform.fields.keys():
    #    data.append([key, unicode(cfform.cleaned_data[key])])
    
    tmpl_html_body = loader.get_template(mail_templates[0])
    tmpl_plain_body = loader.get_template(mail_templates[1])

    c = Context({"data": data, "subject":subject, "user": user, "name":name, "datum": datetime.now()})
    html_content = tmpl_html_body.render(c)
    plain_content = tmpl_plain_body.render(c)
    
    msg = mailer.GenerateMessage(name, "noreply@active8.nl", replyto_name, reply_to, "A friend", tomail, subject, html_content, plain_content, [])
    result = mailer.SendMessage("noreply@active8.nl", [tomail], msg)
    
    return errorstr


if __name__ == '__main__':
    
    print mailDrop("4d5970b8ca6a007f34000002", "noreply@active8.nl", "noreply@active8.nl", "erik@a8.nl", ("drop_share_html.html", "drop_share_txt.html"), "error string", "noreply")
    