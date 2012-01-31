import settings
import time
import codecs
import argparse
import re

import json, urllib2

import sqlite3
import sys

conn = None
c = None

def setupdb() :
    global conn
    global c

    conn = sqlite3.connect('link.db')

    c = conn.cursor()

    try:
        c.execute('''create table if not exists lastupdate (id integer, updatetime varchar)''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create lastupdate"

def addgroup(id):
    #XXX injection problem potentially
    try:
        c.execute('''create table if not exists fbgroup_''' + id + '''  (url varchar, likes integer, unique(url))''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create group"


def addlink(id, url, likes):
    try:
        c.execute("insert or ignore into fbgroup_" + id + " values (?, ?)", (url, likes))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on link insert"

def getlastupdate(id):
    date = ''
    try:
        c.execute("select updatetime from lastupdate where id={0}".format(id))
        rows = c.fetchall()
        for row in rows:
            date = time.strptime(row['updatetime'], '%Y-%m-%dT%H:%M:%S+0000')
        return date
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on lastudpate select"
            
def nsbmkhdr(name):
    hdr = u''
    hdr += '<!DOCTYPE NETSCAPE-Bookmark-file-1>\n'
    hdr += '<!-- This is an automatically generated file.\n'
    hdr += '     It will be read and overwritten.\n'
    hdr += '     DO NOT EDIT! -->\n'
    hdr += '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n'
    hdr += '<TITLE>Bookmarks</TITLE>\n'
    hdr += '<H1>Bookmarks</H1>\n'
    hdr += '<DL><p>\n'
    hdr += '    <DT><H3 ADD_DATE="1323724657" LAST_MODIFIED="1323724657">{0}</H3>\n'.format(name)
    hdr += '    <DL><p>\n'

    return hdr

def link2nsbmk(link):
    return u'        <DT><A HREF="{0}" ADD_DATE="1323724657">{1}</A>\n'.format(link,link)

def nsbmkftr():
    ftr = u''
    ftr = '    </DL><p>\n'
    ftr = '</DL><p>\n'

    return ftr

def feedlinks(doc, groupid):
    links = []
    lastupdate = getlastupdate(groupid)
    print lastupdate
    urlre = re.compile("http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?")
    for post in doc['data']:
        #date = time.strptime(post['updated_time'], '%Y-%m-%dT%H:%M:%S+0000')
        #print date
        try:
            matches = urlre.finditer(post['message'])
            if matches:
                for match in matches:
                    addlink(groupid,match.group(0),0)
                    links.append(match.group(0))
        except KeyError:
            pass
        try:
            addlink(groupid,post['link'],0)
            links.append(post['link'])
        except KeyError:
            pass

        try:
            if len(post['comments']['data']) < post['comments']['count']:
                commenturl = settings.fb_graph_url + '/' + post['id'] + '/' + 'comments' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(post['comments']['count'])
                commentreq = json.loads(urllib2.urlopen(commenturl).read())
                for comment in commentreq['data']:
                    matches = urlre.finditer(comment['message'])
                    if matches:
                        for match in matches:
                            addlink(groupid,match.group(0),0)
                            links.append(match.group(0))
            else:
                for comment in post['comments']['data']:
                    matches = urlre.finditer(comment['message'])
                    if matches:
                        for match in matches:
                            addlink(groupid,match.group(0),0)
                            links.append(match.group(0))
        except KeyError:
            pass

    return links

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-p', '--pages', dest='feed_pages', type=int, default=settings.feed_pages)
parser.add_argument('-f', '--format', dest='format', default=settings.bookmark_format)
parser.add_argument('-n', '--name', dest='name', default=settings.bookmark_title)
parser.add_argument('-u', '--update', dest='lastupdate', default=None)

args = parser.parse_args()

print 'Dumping links from {0} pages'.format(args.feed_pages)

next = feedurl
pagecount = 0

links = []
setupdb()
addgroup(settings.fb_group_id)

while True:
    doc = json.loads(urllib2.urlopen(next).read())
    try:
        next = doc['paging']['next']
    except KeyError:
        break
    links.extend(feedlinks(doc, settings.fb_group_id))
    pagecount += 1
    print 'Processed page {0}'.format(pagecount)
    if pagecount >= args.feed_pages:
        break

ulinks = set(links)

if args.format == 'ns':
    type = '.html'
else:
    type = '.txt'

f = codecs.open(settings.fb_group_id + type, encoding='utf-8', mode='w+')

if args.format == 'ns':
    f.write(nsbmkhdr(args.name))

for link in ulinks:
    if args.format == 'ns':
        f.write(link2nsbmk(link))
    else:
        f.write(link + '\n')

if args.format == 'ns':
    f.write(nsbmkftr())

f.close()
