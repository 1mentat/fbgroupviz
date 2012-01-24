import settings
import time
import codecs
import argparse
import dokuwiki as wiki

import json, urllib2

def post2gdf(doc):
    nodedoc = unicode('')
    edgedoc = unicode('')
    people = dict()
    nodedoc += 'nodedef> name VARCHAR,label VARCHAR,type VARCHAR\n'
    edgedoc += 'edgedef> node1 VARCHAR,node2 VARCHAR,weight DOUBLE\n'
    try:
        nodedoc += '{0},{1},{2}\n'.format('id_' + doc['id'],'post','post')
        edgedoc += '{0},{1},{2}\n'.format('id_' + doc['from']['id'],'id_' + doc['id'],'.8')
        people[doc['from']['id']] = doc['from']['name']
    except KeyError:
        nodedoc += '{0},{1},{2}\n'.format('Unknown','post','post')

    try:
        if len(doc['likes']['data']) < doc['likes']['count']:
            likeurl = settings.fb_graph_url + '/' + doc['id'] + '/' + 'likes' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(doc['likes']['count'])
            likereq = json.loads(urllib2.urlopen(likeurl).read())
            for like in likereq['data']:
                people[like['id']] = like['name']
                edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + doc['id'],'.3')
        else:
            for like in doc['likes']['data']:
                people[like['id']] = like['name']
                edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + doc['id'],'.3')
    except KeyError:
        pass

    try:
        if len(doc['comments']['data']) < doc['comments']['count']:
            commenturl = settings.fb_graph_url + '/' + doc['id'] + '/' + 'comments' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(doc['comments']['count'])
            commentreq = json.loads(urllib2.urlopen(commenturl).read())
            for comment in commentreq['data']:
                people[comment['from']['id']] = comment['from']['name']
                nodedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'c','comment')
                edgedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'id_' + doc['id'],'.6')
                edgedoc += '{0},{1},{2}\n'.format('id_' + comment['from']['id'],'id_' + comment['id'],'.8')
#                try:
#                    if comment['likes']:
#                        likeurl = settings.fb_graph_url + '/' + comment['id'] + '/' + 'likes' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(comment['likes'])
#                        likereq = json.loads(urllib2.urlopen(likeurl).read())
#                        for like in likereq['data']:
#                            people[like['id']] = like['name']
#                            edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + comment['id'],'.3')
#                except KeyError:
#                    pass
        else:
            for comment in doc['comments']['data']:
                people[comment['from']['id']] = comment['from']['name']
                nodedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'c','comment')
                edgedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'id_' + doc['id'],'.6')
                edgedoc += '{0},{1},{2}\n'.format('id_' + comment['from']['id'],'id_' + comment['id'],'.8')
#                try:
#                    if comment['likes']:
#                        likeurl = settings.fb_graph_url + '/' + comment['id'] + '/' + 'likes' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(comment['likes'])
#                        likereq = json.loads(urllib2.urlopen(likeurl).read())
#                        for like in likereq['data']:
#                            people[like['id']] = like['name']
#                            print like['name']
#                            edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + comment['id'],'.3')
#                except KeyError:
#                    pass
    except KeyError:
        pass

    for id in people.keys():
        nodedoc += u'{0},{1},{2}\n'.format('id_' + id, people[id],'person')

    return nodedoc, edgedoc

parser = argparse.ArgumentParser(description='Options')
parser.add_argument('-p', '--post', dest='post_id', default=settings.fb_post_id)

args = parser.parse_args()

posturl = settings.fb_graph_url + '/' + args.post_id + '/' + '?' + settings.fb_oauth_token

doc = json.loads(urllib2.urlopen(posturl).read())
(nodedoc, edgedoc) = post2gdf(doc)

f = codecs.open(args.post_id + '.gdf', encoding='utf-8', mode='w+')
f.write(nodedoc)
f.write(edgedoc)
