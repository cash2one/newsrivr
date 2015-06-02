# -*- coding: iso-8859-1 -*
##
## (c) Fry-IT, www.fry-it.com, 2007
## <peter@fry-it.com>
##

"""
A very spartan attempt of a script that converts HTML to
plaintext.

The original use for this little script was when I send HTML emails out I also
wanted to send a plaintext version of the HTML email as multipart. Instead of 
having two methods for generating the text I decided to focus on the HTML part
first and foremost (considering that a large majority of people don't have a 
problem with HTML emails) and make the fallback (plaintext) created on the fly.

This little script takes a chunk of HTML and strips out everything except the
<body> (or an elemeny ID) and inside that chunk it makes certain conversions 
such as replacing all hyperlinks with footnotes where the URL is shown at the
bottom of the text instead. <strong>words</strong> are converted to *words* 
and it does a fair attempt of getting the linebreaks right.

As a last resort, it strips away all other tags left that couldn't be gracefully
replaced with a plaintext equivalent.
Thanks for Fredrik Lundh's unescape() function things like:
    'Terms &amp; Conditions' is converted to
    'Termss & Conditions'

It's far from perfect but a good start. It works for me for now.


TODO: 
    * proper unit tests
    * understand some basic style commands such as font-weight:bold 

    
Announcement here:
    http://www.peterbe.com/plog/html2plaintext
    
Thanks to:
    Philipp (http://www.peterbe.com/plog/html2plaintext#c0708102y47)
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import chr

__version__='0.2'


import re, sys
from BeautifulSoup import BeautifulSoup, SoupStrainer, Comment

def html2plaintext(html, body_id=None, encoding='utf-8'):
    """ from an HTML text, convert the HTML to plain text.
    If @body_id is provided then this is the tag where the 
    body (not necessarily <body>) starts.
    """
    urls = []
    if body_id is not None:
        strainer = SoupStrainer(id=body_id)
    else:
        strainer = SoupStrainer()
    
    """
    soup = BeautifulSoup(html, parseOnlyThese=strainer, fromEncoding=encoding)
    for link in soup.findAll('a'):
        title = link.renderContents()
        for url in [x[1] for x in link.attrs if x[0]=='href']:
            urls.append(dict(url=url, tag=str(link), title=title))

    html = soup.__str__(encoding)
            
    url_index = []
    i = 0
    for d in urls:
        if d['title'] == d['url'] or 'http://'+d['title'] == d['url']:
            html = html.replace(d['tag'], d['url'])
        else:
            i += 1
            html = html.replace(d['tag'], '%s [%s]' % (d['title'], i))
            url_index.append(d['url'])
    """
    
    html = html.replace('<a', 'HREFOPEN').replace('</a>', 'HREFCLOSE')
    html = html.replace('<strong>','*').replace('</strong>','*')
    html = html.replace('<b>','*').replace('</b>','*')
    html = html.replace('<h3>','*').replace('</h3>','*')
    html = html.replace('<p>','PARAOPEN').replace('</p>','PARACLOSE')
    html = html.replace('<h2>','ITALICOPEN').replace('</h2>','ITALICCLOSE')
    html = html.replace('<h1>','BOLDOPEN').replace('</h1>','BOLDCLOSEBREAKBREAK')
    html = html.replace('<em>','/').replace('</em>','/')
    

    # the only line breaks we respect is those of ending tags and 
    # breaks
    
    html = html.replace('\n',' ')
    html = html.replace('<br>', '\n')
    #html = html.replace('</p>', '\n')
    html = re.sub('<br\s*/>', '\n', html)
    html = html.replace(' ' * 2, ' ')


    # for all other tags we failed to clean up, just remove then and 
    # complain about them on the stderr
    def desperate_fixer(g):
        #print >>sys.stderr, "failed to clean up %s" % str(g.group())
        return ' '

    html = re.sub('<.*?>', desperate_fixer, html)
    
    html = html.replace('ITALICOPEN', '\n\n<i>')
    html = html.replace('ITALICCLOSE', '</i>\n\n')
    html = html.replace('BOLDOPEN', '<b>')
    html = html.replace('BOLDCLOSEBREAKBREAK', '</b>\n\n')
    html = html.replace('PARAOPEN', '')    
    html = html.replace('PARACLOSE', '')
    html = html.replace('HREFOPEN', '<a')
    html = html.replace('HREFCLOSE', '</a>')
    
    # lstrip all lines
    html = '\n'.join([x.lstrip() for x in html.splitlines()])
    
    
    #for i, url in enumerate(url_index):
    #    if i == 0:
    #        html += '\n\n'
    #    html += '[%s] %s\n' % (i+1, url)

    html = unescape(html)
    
    return html

import html.entities
# from http://effbot.org/zone/re-sub.htm#strip-html
##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)



def test_html2plaintest():
    html = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<body>

<div id="main">
<p>This is a paragraph.</p>

<p><a href="http://one.com">Foobar</a>
<br />

<a href="http://two.com">two.com</a>

</p>
     <p>Visit <a href="http://www.google.com">www.google.com</a>.</p>
<br />
Text elsewhere.

<a href="http://three.com">Elsewhere</a>

</div>
</body>
</html>
    '''
    print(html2plaintext(html, body_id='main'))

    
if __name__=='__main__':
    test_html2plaintest()