import settings
#import memberdb
#import graphdb
import time
import codecs

import json, urllib2

def feed2wiki(doc):
    postdoc = ''

    for post in doc['data']:
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

    return postdoc

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token
groupurl = settings.fb_graph_url + '/' + settings.fb_group_id + '?' + settings.fb_oauth_token

#memberdb.setupdb()
#graphdb.setup_db()

f = codecs.open('{0}.feed'.format(settings.fb_group_id), encoding='utf-8', mode='w+')

postdoc=""
heading1 = "===== "
heading2 = "==== "

doc = json.loads(urllib2.urlopen(feedurl).read())
next = doc['paging']['next']

postdoc += feed2wiki(doc)

doc = json.loads(urllib2.urlopen(next).read())

postdoc += feed2wiki(doc)

f.write(postdoc)
f.close()

