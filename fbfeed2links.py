import settings
import time
import codecs
import argparse
import re

import json, urllib2

def feedlinks(doc):
    links = []
    urlre = re.compile("http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?")
    for post in doc['data']:
        try:
            matches = urlre.finditer(post['message'])
            if matches:
                for match in matches:
                    links.append(match.group(0))
        except KeyError:
            pass
        try:
            links.append(post['link'])
        except KeyError:
            pass
        try:
            links.append(post['picture'])
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
                            links.append(match.group(0))
            else:
                for comment in post['comments']['data']:
                    matches = urlre.finditer(comment['message'])
                    if matches:
                        for match in matches:
                            links.append(match.group(0))
        except KeyError:
            pass

    return links

feedurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'feed' + '?' + settings.fb_oauth_token

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-p', '--pages', dest='feed_pages', type=int, default=settings.feed_pages)

args = parser.parse_args()

print 'Dumping links from {0} pages'.format(args.feed_pages)

next = feedurl
pagecount = 0

links = []

while True:
    #this probably doesn't handle next returning 'data' that's empty well
    doc = json.loads(urllib2.urlopen(next).read())
    next = doc['paging']['next']
    links.extend(feedlinks(doc))
    pagecount += 1
    print 'Processed page {0}'.format(pagecount)
    if pagecount >= args.feed_pages:
        break

for link in links:
    print link
