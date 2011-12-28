import urllib2
import urllib
import settings
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text

def isEditForm(f):
    try:
        if f.attrs['id'] == 'dw__editform':
            return True
    except KeyError:
        return False

def changepage(pagename,newtext):
    values = {}
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

    values['do'] = 'edit'
    values['rev'] = ''
    values['id'] = pagename

    data = urllib.urlencode(values)

    br.open(url,data)
    br.select_form(predicate=isEditForm)
    br.form['wikitext'] = newtext
    br.submit()

if __name__ == '__main__':
    newchangepage('test','testing')
