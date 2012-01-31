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
        c.execute('''create table if not exists lastupdate (id integer, updatetime varchar, unique(id))''')
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
    date = time.gmtime(0)
    try:
        c.execute("select updatetime from lastupdate where id={0}".format(id))
        rows = c.fetchall()
        for row in rows:
            date = time.strptime(row[0], '%Y-%m-%dT%H:%M:%S+0000')
        return date
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on lastudpate select"

def setlastupdate(id,date):
    textdate = time.strftime('%Y-%m-%dT%H:%M:%S+0000',date)
    print 'setting new lastupdate to {0}'.format(textdate)
    try:
        c.execute("insert or ignore into lastupdate values (?, ?)", (id, textdate))
        c.execute("update lastupdate set updatetime=? WHERE id=?", (textdate, id))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on link insert"

def linkdb2nsbmk(id):
    linktext = u''
    try:
        c.execute("select url from fbgroup_" + id)
        rows = c.fetchall()
        for row in rows:
            linktext += link2nsbmk(row[0])
        return linktext
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on linkdb select"
            
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

def feedlinks(doc, groupid, links):
    data = u''
    shortcircuit = False
    lastupdate = getlastupdate(groupid)
    newlastupdate = time.gmtime(0)
    urlre = re.compile("http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?")
    for post in doc['data']:
        date = time.strptime(post['updated_time'], '%Y-%m-%dT%H:%M:%S+0000')
        #print 'date: {0} lastupdate: {1} newlastupdate: {2}'.format(date,lastupdate,newlastupdate)
        if date > lastupdate:
            if date > newlastupdate:
                newlastupdate = date
        else:
            if lastupdate > newlastupdate:
                newlastupdate = lastupdate
            if args.fullupdate == False:
                shortcircuit = True
                break
        try:
            matches = urlre.finditer(post['message'])
            if matches:
                for match in matches:
                    if match.group(0) not in links:
                        links.add(match.group(0))
                        data += link2nsbmk(match.group(0))
                    addlink(groupid,match.group(0),0)
        except KeyError:
            pass
        try:
            if post['link'] not in links:
                links.add(post['link'])
                data += post['link']
            addlink(groupid,post['link'],0)
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
                            if match.group(0) not in links:
                                links.add(match.group(0))
                                data += link2nsbmk(match.group(0))
                            addlink(groupid,match.group(0),0)
            else:
                for comment in post['comments']['data']:
                    matches = urlre.finditer(comment['message'])
                    if matches:
                        for match in matches:
                            if match.group(0) not in links:
                                links.add(match.group(0))
                                data += link2nsbmk(match.group(0))
                            addlink(groupid,match.group(0),0)
        except KeyError:
            pass

    return links, newlastupdate, data, shortcircuit

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-n', '--name', dest='name', default=settings.bookmark_title)
parser.add_argument('-u', '--fullupdate', dest='fullupdate', action='store_true', default=False)

args = parser.parse_args()

next = feedurl
pagecount = 0

links = set()
setupdb()
addgroup(settings.fb_group_id)
newlastupdate = time.gmtime(0)

f = codecs.open(settings.fb_group_id + 'html', encoding='utf-8', mode='w+')

f.write(nsbmkhdr(args.name))

if args.fullupdate == False:
    linktext = linkdb2nsbmk(settings.fb_group_id)
    if linktext:
        f.write(linktext)

while True:
    linkstext = u''
    doc = json.loads(urllib2.urlopen(next).read())
    try:
        next = doc['paging']['next']
    except KeyError:
        break
    (newlinks, lastupdate, linkstext, shortcircuit) = feedlinks(doc, settings.fb_group_id, links)
    f.write(linkstext)
    links.update(newlinks)
    if lastupdate > newlastupdate:
        newlastupdate = lastupdate
    pagecount += 1
    print 'Processed page {0}'.format(pagecount)
    if shortcircuit:
        break

setlastupdate(settings.fb_group_id,newlastupdate)

f.write(nsbmkftr())

f.close()
