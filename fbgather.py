import settings
import memberdb
import graphdb
import time

import json, urllib2

membersurl = settings.fb_graph_url + '/' + settings.fb_group_id + '/' + 'members' + '?' + settings.fb_oauth_token
groupurl = settings.fb_graph_url + '/' + settings.fb_group_id + '?' + settings.fb_oauth_token

memberdb.setupdb()
graphdb.setup_db()

#this should be automated...
group = graphdb.get_or_create_group('Group Name',settings.fb_group_id,'fb_group')

for member in json.loads(urllib2.urlopen(membersurl).read())['data']:
    link=''
    memberdb.addmember(member['id'],member['name'],link)
    member['fb_id'] = member['id']
    person = graphdb.get_or_create_person(member)
    graphdb.add_member_to_group(person,group)
    print unicode("Add member {0} with id {1} to FB group {2}").format(member['name'],member['id'],settings.fb_group_id)
