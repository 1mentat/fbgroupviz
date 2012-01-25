import settings
import time
import codecs
import argparse
import dokuwiki as wiki
import json, urllib2

class PostGDF:
    """The GDF based on a FB Post"""
    nodedoc = unicode('')
    edgedoc = unicode('')
    people = dict()
    pst2pstrW = '.3'
    psn2cmntW = '.5'
    psn2postW = '.5'
    tag2psnW = '.5'
    cmnt2postW = '1'

    def dopost(self):
        try:
            likes = '0'
            try:
                likes = self.doc['likes']['count']
            except KeyError:
                pass
            self.nodedoc += '{0},{1},{2},{3}\n'.format('id_' + self.doc['id'],'post','post',likes)
            self.edgedoc += '{0},{1},{2}\n'.format('id_' + self.doc['from']['id'],'id_' + self.doc['id'],self.pst2pstrW)
            self.people[self.doc['from']['id']] = self.doc['from']['name']
        except KeyError:
            self.nodedoc += '{0},{1},{2},{3}\n'.format('Unknown','post','post','0')

    def dolikes(self):
        try:
            if len(self.doc['likes']['data']) < self.doc['likes']['count']:
                likeurl = settings.fb_graph_url + '/' + self.doc['id'] + '/' + 'likes' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(self.doc['likes']['count'])
                likereq = json.loads(urllib2.urlopen(likeurl).read())
                for like in likereq['data']:
                    self.people[like['id']] = like['name']
                    self.edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + self.doc['id'],self.psn2postW)
            else:
                for like in self.doc['likes']['data']:
                    self.people[like['id']] = like['name']
                    self.edgedoc += '{0},{1},{2}\n'.format('id_' + like['id'],'id_' + self.doc['id'],self.psn2postW)
        except KeyError:
            pass

    def docomment(self,comment):
        self.people[comment['from']['id']] = comment['from']['name']
        likes = '0'
        try:
            likes = comment['likes']
        except KeyError:
            pass
        self.nodedoc += '{0},{1},{2},{3}\n'.format('id_' + comment['id'],'c','comment',likes)
        self.edgedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'id_' + self.doc['id'],self.cmnt2postW)
        self.edgedoc += '{0},{1},{2}\n'.format('id_' + comment['from']['id'],'id_' + comment['id'],self.psn2cmntW)
        try:
            for tag in comment['message_tags']:
                self.people[tag['id']] = tag['name']
                self.edgedoc += '{0},{1},{2}\n'.format('id_' + comment['id'],'id_' + tag['id'],self.tag2psnW)
        except KeyError:
            pass

    def docomments(self):
        try:
            if len(self.doc['comments']['data']) < self.doc['comments']['count']:
                commenturl = settings.fb_graph_url + '/' + self.doc['id'] + '/' + 'comments' + '?' + settings.fb_oauth_token + '&' + 'limit={0}'.format(self.doc['comments']['count'])
                commentreq = json.loads(urllib2.urlopen(commenturl).read())
                for comment in commentreq['data']:
                    self.docomment(comment)
            else:
                for comment in self.doc['comments']['data']:
                    self.docomment(comment)
        except KeyError:
            pass

    def render(self):
        self.dopost()
        self.dolikes()
        self.docomments()

    def __init__(self, doc=''):
        self.nodedoc += 'nodedef> name VARCHAR,label VARCHAR,type VARCHAR, likes INT\n'
        self.edgedoc += 'edgedef> node1 VARCHAR,node2 VARCHAR,weight DOUBLE\n'
        self.doc = doc

    def addPost(self, doc):
        self.doc = doc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-p', '--post', dest='post_ids', action='append', default=[])
    parser.add_argument('-o', '--output', dest='output', default='post')

    args = parser.parse_args()

    if args.post_ids == []:
        args.post_ids = settings.fb_post_id

    print args.post_ids

    thepost = PostGDF()

    for post_id in args.post_ids:
        print 'Processing post id {0}'.format(post_id)

        posturl = settings.fb_graph_url + '/' + post_id + '/' + '?' + settings.fb_oauth_token

        doc = json.loads(urllib2.urlopen(posturl).read())

        thepost.addPost(doc)

        thepost.render()

    for id in thepost.people.keys():
        thepost.nodedoc += u'{0},{1},{2},{3}\n'.format('id_' + id, thepost.people[id],'person','0')

    f = codecs.open(args.output + '.gdf', encoding='utf-8', mode='w+')
    f.write(thepost.nodedoc)
    f.write(thepost.edgedoc)
