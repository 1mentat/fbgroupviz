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
            postdoc += 'Likes : '
            if len(post['likes']['data']) < post['likes']['count']:
                likeurl = settings.fb_graph_url + '/' + post['id'] + '/' + 'likes' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(post['likes']['count'])
                likereq = json.loads(urllib2.urlopen(likeurl).read())
                for like in likereq['data']:
                    postdoc += like['name'] + ', '
            else:
                for like in post['likes']['data']:
                    postdoc += like['name'] + ', '
            postdoc += '\n\n'
        except KeyError:
            postdoc += 'None\n\n'

        try:
            if len(post['comments']['data']) < post['comments']['count']:
                commenturl = settings.fb_graph_url + '/' + post['id'] + '/' + 'comments' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(post['comments']['count'])
                commentreq = json.loads(urllib2.urlopen(commenturl).read())
                for comment in commentreq['data']:
                    postdoc += heading3 + comment['from']['name'] + heading3 + '\n\n'
                    postdoc += comment['message'] + '\n\n'
            else:
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
