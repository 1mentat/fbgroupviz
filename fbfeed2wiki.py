import settings
import time
import codecs
import dokuwiki

import json, urllib2

def feed2wiki(cj,doc):
    for post in doc['data']:
        postdoc = unicode('')
        postdoc += headingthreadmode
        postdoc += heading2
        try:
            postdoc += post['from']['name']
        except KeyError:
            postdoc += 'Unknown'
        postdoc += heading2 + '\n\n'

        try:
            postdoc += post['message'] + '\n\n'
        except KeyError:
            postdoc += 'No message\n\n'
        try:
            postdoc += 'Link: [[' + post['link'] + ']]\n\n'
        except KeyError:
            pass
        try:
            postdoc += '{{' + post['picture'] + ' }}\n\n'
        except KeyError:
            pass

        try:
            for comment in post['comments']['data']:
                postdoc += heading3 + comment['from']['name'] + heading3 + '\n\n'
                postdoc += comment['message'] + '\n\n'
        except KeyError:
            postdoc += 'No Comments\n\n'

        dokuwiki.changepage(cj,settings.wiki_prefix + post['id'],postdoc.encode('utf-8'))

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token
groupurl = settings.fb_graph_url + '/' + settings.fb_group_id + '?' + settings.fb_oauth_token

headingthreadmode = '===== Thread Mode =====\n'
heading1 = "==== "
heading2 = "=== "
heading3 = "== "

cj = dokuwiki.login(settings.wiki_user,settings.wiki_pw)

doc = json.loads(urllib2.urlopen(feedurl).read())
next = doc['paging']['next']

feed2wiki(cj,doc)

doc = json.loads(urllib2.urlopen(next).read())

feed2wiki(cj,doc)
