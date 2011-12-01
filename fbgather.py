import settings
import memberdb
import time

import json, urllib2

url = settings.fb_group_url + 'members' + settings.fb_oauth_token

memberdb.setupdb()

for member in json.loads(urllib2.urlopen(url).read())['data']:
    try:
        link = json.loads(urllib2.urlopen("https://graph.facebook.com/" + member['id']).read())['link']
    except:
        print "Unable get get " + "https://graph.facebook.com/" + member['id']
        link = ""
    memberdb.addmember(member['id'],member['name'],link)
    print unicode("    {0} [label=\"{1}\", href=\"{2}\"]\n").format(int(member['id']),member['name'],link)
