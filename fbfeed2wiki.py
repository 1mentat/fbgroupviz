import settings
#import memberdb
#import graphdb
import time
import codecs

import json, urllib2

def feed2wiki(doc):
    for post in doc['data']:
        postdoc = ''
        f = codecs.open('posts/{0}.post'.format(post['id']), encoding='utf-8', mode='w+')
        postdoc += headingdocmode
        postdoc += headingthreadmode
        postdoc += heading1
        postdoc += "Post"
        postdoc += heading1 + '\n'
        postdoc += heading2
        try:
            postdoc += "From: " + post['from']['name']
        except KeyError:
            postdoc += 'From: Unknown'
        postdoc += heading2 + '\n'
        try:
            postdoc += '<file>' + post['message'] + '</file>' + '\n'
        except KeyError:
            postdoc += 'No message\n\n'
        try:
            postdoc += 'Link: [[' + post['link'] + ']]\n\n'
        except KeyError:
            postdoc += 'No link\n'

        f.write(postdoc)
        f.close()

    return postdoc

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token
groupurl = settings.fb_graph_url + '/' + settings.fb_group_id + '?' + settings.fb_oauth_token

#memberdb.setupdb()
#graphdb.setup_db()

headingdocmode = '===== Document Mode =====\n'
headingthreadmode = '===== Thread Mode =====\n'
heading1 = "==== "
heading2 = "=== "

doc = json.loads(urllib2.urlopen(feedurl).read())
next = doc['paging']['next']

feed2wiki(doc)

doc = json.loads(urllib2.urlopen(next).read())

feed2wiki(doc)
