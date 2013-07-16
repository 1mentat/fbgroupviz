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

    conn = sqlite3.connect('comment.db')

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
        c.execute('''create table if not exists fbgroup_''' + id + '''  (comment varchar, likes integer, unique(comment))''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create group"


def addcomment(id, comment, likes):
    try:
        c.execute("insert or ignore into fbgroup_" + id + " values (?, ?)", (comment, likes))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on comment insert"

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

def feedcomments(doc, groupid, targetid):
    shortcircuit = False
    lastupdate = getlastupdate(groupid)
    newlastupdate = time.gmtime(0)
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
            if post['from']['id'] == targetid:
                print u"You ({}) wrote {}".format(post['from']['name'],post['message'])
                addcomment(groupid,post['message'],0)
        except KeyError:
            pass

        try:
            if len(post['comments']['data']) < post['comments']['count']:
                commenturl = settings.fb_graph_url + '/' + post['id'] + '/' + 'comments' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(post['comments']['count'])
                commentreq = json.loads(urllib2.urlopen(commenturl).read())
                for comment in commentreq['data']:
                    if comment['from']['id'] == targetid:
                        print u"You ({}) wrote {}".format(comment['from']['name'],comment['message'])
                        addcomment(groupid,comment['message'],0)
            else:
                for comment in post['comments']['data']:
                    if comment['from']['id'] == targetid:
                        print u"You ({}) wrote {}".format(comment['from']['name'],comment['message'])
                        addcomment(groupid,comment['message'],0)
        except KeyError:
            pass

    return newlastupdate, shortcircuit

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-u', '--fullupdate', dest='fullupdate', action='store_true', default=False)
parser.add_argument('-m', '--me', dest='targetid', default=settings.fb_person_id)

args = parser.parse_args()

next = feedurl
pagecount = 0

setupdb()
addgroup(settings.fb_group_id)
newlastupdate = time.gmtime(0)

while True:
    doc = json.loads(urllib2.urlopen(next).read())
    try:
        next = doc['paging']['next']
    except KeyError:
        break
    (lastupdate, shortcircuit) = feedcomments(doc, settings.fb_group_id, args.targetid)
    if lastupdate > newlastupdate:
        newlastupdate = lastupdate
    pagecount += 1
    print 'Processed page {0}'.format(pagecount)
    if shortcircuit:
        break

setlastupdate(settings.fb_group_id,newlastupdate)
