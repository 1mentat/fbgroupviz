import settings
import time
import codecs
import argparse
import dokuwiki as wiki

import json, urllib2

def feed2wiki(cj,doc):
    ididx = []
    for post in doc['data']:
        postdoc = unicode('')
        postdoc += wiki.headingthreadmode
        postdoc += wiki.heading2
        try:
            postdoc += post['from']['name']
        except KeyError:
            postdoc += 'Unknown'
        postdoc += wiki.heading2 + '\n\n'

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
                    postdoc += wiki.heading3 + comment['from']['name'] + wiki.heading3 + '\n\n'
                    postdoc += comment['message'] + '\n\n'
            else:
                for comment in post['comments']['data']:
                    postdoc += wiki.heading3 + comment['from']['name'] + wiki.heading3 + '\n\n'
                    postdoc += comment['message'] + '\n\n'
        except KeyError:
            postdoc += 'No Comments\n\n'

        wiki.changepage(cj,settings.wiki_prefix + post['id'],postdoc.encode('utf-8'))

        ididx.append(post['id'])
    return ididx

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token
groupurl = settings.fb_graph_url + '/' + settings.fb_group_id + '?' + settings.fb_oauth_token

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-p', '--pages', dest='feed_pages', type=int, default=settings.feed_pages)

args = parser.parse_args()

print 'Mirroring {0} pages'.format(args.feed_pages)

cj = wiki.login(settings.wiki_user,settings.wiki_pw)

next = feedurl
pagecount = 0

ididx = []

while True:
    #this probably doesn't handle next returning 'data' that's empty well
    doc = json.loads(urllib2.urlopen(next).read())
    next = doc['paging']['next']
    ididx.extend(feed2wiki(cj,doc))
    pagecount += 1
    print 'Processed page {0}'.format(pagecount)
    if pagecount >= args.feed_pages:
        break

indexdoc = unicode('')
indexdoc += wiki.headingthreadmode
indexdoc += wiki.heading2 + settings.wiki_prefix + ' Index' + wiki.heading2 + '\n\n'
for id in ididx:
    indexdoc += '[[' + settings.wiki_prefix + id + ']]\n\n'
wiki.changepage(cj,settings.wiki_prefix,indexdoc.encode('utf-8'))
