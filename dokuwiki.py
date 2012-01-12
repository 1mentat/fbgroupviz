import urllib2
import urllib
import settings
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import re

def isEditForm(f):
    try:
        if f.attrs['id'] == 'dw__editform':
            return True
    except KeyError:
        return False

def isLoginButton(f):
    try:
        if f.attrs['class'] == 'button btn_login':
            return True
    except KeyError:
        return False

def isLoginForm(f):
    try:
        if f.attrs['id'] == 'dw__login':
            return True
    except KeyError:
        return False

def changepage(cj, pagename, newtext):
    values = {}
    br = mechanize.Browser()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    
    url = settings.wiki_url

    values['do'] = 'edit'
    values['rev'] = ''
    values['id'] = pagename

    data = urllib.urlencode(values)

    getdoc = re.compile('(===== Document Mode =====)(.*)(===== Thread Mode =====)(.*)', re.S)

    br.open(url,data)
    br.select_form(predicate=isEditForm)
    result = getdoc.match(br.form['wikitext'])
    if result != None:
        br.form['wikitext'] = '===== Document Mode =====' + result.group(2) + newtext
    else:
        br.form['wikitext'] = '===== Document Mode =====' + '\n\n' + newtext
    br.submit()

def login(username,password):
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    url = settings.wiki_url

    br.open(url)
    br.select_form(predicate=isLoginButton)
    br.submit()
    br.select_form(predicate=isLoginForm)
    br.form['u'] = username
    br.form['p'] = password
    br.submit()
    
    return cj

headingthreadmode = '===== Thread Mode =====\n'
heading1 = "==== "
heading2 = "=== "
heading3 = "== "

if __name__ == '__main__':
    cj = login(settings.wiki_user,settings.wiki_pw)
    changepage(cj,'test','===== Thread Mode =====\n\ntesting\n\n')
