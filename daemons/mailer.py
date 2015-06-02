
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import utils, encoders
import mimetypes
from django.template import Context, Template
import os
import os.path

def determine_encoding(text):
    possible_charsets = ['US-ASCII', 'ISO-8859-1', 'UTF-8']
    for charset in possible_charsets:
        try:
            text.encode(charset)
        except UnicodeError:
            pass
        else:
            return charset
            break
    
    error_msg = "Unable to determine the correct encoding. Please ensure that a encoding into one of %s is possible." % (possible_charsets, )
    raise Exception( error_msg )    
    
def GenerateMessage(from_name, from_email, reply_to_name, reply_to_email, to_name, to_email, subject, html_body, plain_body, attachments):
  
    from_hdr = utils.formataddr( (from_name, from_email ) ) if len(from_name) > 0 else utils.formataddr( (False, from_email) )
    reply_to_hdr = utils.formataddr( (reply_to_name, reply_to_email) ) if len(reply_to_name) > 0 else utils.formataddr( (False, reply_to_name) )
    to_hdr   = utils.formataddr( (to_name, to_email) ) if len(to_name) > 0 else utils.formataddr( (False, to_name) )
 
    from_hdr_charset = determine_encoding(from_hdr)
    reply_to_hdr_charset = determine_encoding(reply_to_hdr)
    to_hdr_charset = determine_encoding(to_hdr)
    subject_charset = determine_encoding(subject)
    
    html_body_charset = determine_encoding(html_body)
    plain_body_charset = determine_encoding(plain_body)
        
    # Create message container - This one will house the 'multipart alternative part' and the 'attachments part'.
    root_msg = MIMEMultipart('mixed')
    root_msg['Subject'] = Header(subject.encode(subject_charset), subject_charset)
    root_msg['From'] = Header(from_hdr.encode(from_hdr_charset), from_hdr_charset)
    root_msg['To'] = Header(to_hdr.encode(to_hdr_charset), to_hdr_charset)
    root_msg["Date"] = Header(utils.formatdate())
    root_msg["Reply-To"] = Header(reply_to_hdr.encode(reply_to_hdr_charset), reply_to_hdr_charset)
    root_msg["Precedence"] =  Header("junk", "US-ASCII")
    root_msg["Auto-Submitted"] = Header("auto-generated", "US-ASCII")
    
    # Create message container - the correct MIME type is multipart/alternative. This will house the HTML and Plain Text body
    msg = MIMEMultipart('alternative')
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(plain_body.encode(plain_body_charset), 'plain', plain_body_charset)
    part2 = MIMEText(html_body.encode(html_body_charset), 'html', html_body_charset)
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)    
    root_msg.attach(msg)
    
    
    for fn in attachments:
        if not os.path.isfile(fn):
            continue
        
        ctype, encoding = mimetypes.guess_type(fn)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(fn)
            content = UnicodeDammit(fp.read())
            content_charset = determine_encoding(content.unicode)
            content = content.unicode.encode(content_charset)
        
            parta = MIMEText(content, _subtype=subtype, _charset=content_charset)
            fp.close()
        elif maintype == 'image':
            fp = open(fn, 'rb')
            parta = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(fn, 'rb')
            parta = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(fn, 'rb')
            parta = MIMEBase(maintype, subtype)
            parta.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            encoders.encode_base64(parta)
        
        # Set the filename parameter
        parta.add_header('Content-Disposition', 'attachment; filename=%s' % os.path.basename(fn))
        root_msg.attach(parta)
    
    return root_msg

def SendMessageFake(*args, **kwargs):
    log.info("Simulate e-mail sending: %s %s" % (args, kwargs,))
    return {}

def SendMessage(from_email, to_list, msg):
    import smtplib
    result = {};    
    mta = smtplib.SMTP('mail.xxx.nl');
    mta.login('xxx', 'xxx');
    
    try:
        result = mta.sendmail(from_email, to_list, msg.as_string());
    except smtplib.SMTPRecipientsRefused, e:
        result = e.recipients;        
    except smtplib.SMTPException, e:
        for email in to_list:
            result[email] = str(e);        
    except Exception, e:
        for email in to_list:
            result[email] = str(e);        
    
        
    try:
        mta.quit();
    except Exception, e:
        pass;
    
    return result