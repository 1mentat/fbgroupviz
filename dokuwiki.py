import urllib2
import urllib
import settings

from HTMLParser import HTMLParser

forms = {}
class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.capturetext = 0
        self.reset()

    def handle_starttag(self, tag, attrs):
        global forms
        try:
            if tag == 'textarea':
                if attrs[0][1] == 'wikitext':
                    self.capturetext = 1
            if attrs[1][0] == 'name':
                if attrs[1][1] == 'sectok':
                    forms['sectok'] = attrs[2][1]
            if attrs[1][0] == 'name':
                if attrs[1][1] == 'changecheck':
                    forms['changecheck'] = attrs[2][1]
        except IndexError:
            pass
    def handle_endtag(self, tag):
        if self.capturetext == 1:
            if tag == 'textarea':
                self.capturetext = 0
#        print "Encountered an end tag:",tag
    def handle_data(self, data):
        if self.capturetext == 1:
            forms['wikitext'] = data

def changepage(pagename,newtext):
    values = {}

    url = settings.wiki_url

    values['do'] = 'edit'
    values['rev'] = ''
    values['id'] = pagename

    parser = MyHTMLParser()

    data = urllib.urlencode(values)
    req = urllib2.Request(url,data)

    try:
        resp = urllib2.urlopen(req)
        parser.feed(resp.read())
    except urllib2.URLError as e:
        print e.reason

    forms['id'] = pagename
    forms['rev'] = ''
    forms['prefix'] = '.'
    forms['suffix'] = ''
    forms['target'] = 'section'
    forms['wikitext'] = newtext
    forms['do[save]'] = 'Save'

    data = urllib.urlencode(forms)
    req = urllib2.Request(url,data)

    try:
        resp = urllib2.urlopen(req)
        #print resp.read() #should verify save successful
    except urllib2.URLError as e:
        print e.reason
