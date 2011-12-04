from neo4j import GraphDatabase
import sys
import settings

def get_or_create_person(new_person):
    #need to add when found to see if other keys require adding
    if new_person['fb_id']:
        for person in people_idx['fb_id'][new_person['fb_id']]:
            print unicode("Name: \"{0}\" FB ID: \"{1}\"").format(person['name'],person['fb_id'])
            return person

        with db.transaction:
            person = db.node(name=new_person['name'],fb_id=new_person['fb_id'])
            person.INSTANCE_OF(people)

            people_idx['name'][new_person['name']] = person
            people_idx['fb_id'][new_person['fb_id']] = person
        return person

def setup_db():
    global db, groups, fbgroups, fbgroups_idx, people, people_idx
    db = GraphDatabase("groupgraphdb")

    with db.transaction:
        try:
            groups = db.reference_node.GROUPS.single.getEndNode()
            print "Groups found"
            print groups
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print 'Creating GROUPS node'
            groups = db.node()
            db.reference_node.GROUPS(groups)
            print groups

        try:
            fbgroups = groups.FBGROUPS.single.getEndNode()
            print "FBGROUPS found"
            print fbgroups
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print 'Creating FBGROUPS node'
            fbgroups = db.node()
            groups.FBGROUPS(fbgroups)
            print fbgroups

        try:
            fbgroups_idx = db.node.indexes.get('fbgroups')
            print 'fbgroups index found'
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print 'Creating fbgroups index'
            fbgroups_idx = db.node.indexes.create('fbgroups')

        try:
            people = db.reference_node.PEOPLE.single.getEndNode()
            print "People found"
            print people
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print 'Creating PEOPLE node'
            people = db.node()
            db.reference_node.PEOPLE(people)

        try:
            people_idx = db.node.indexes.get('people')
            print 'People index found'
        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print 'Creating people index'
            people_idx = db.node.indexes.create('people')

def get_or_create_group(group_name, group_id, group_id_type):
    if group_id_type == 'fb_group':
        for group in fbgroups_idx['id'][group_id]:
            return group

        with db.transaction:
            newgroup = db.node(name=group_name,id=group_id)
            newgroup.member_of(fbgroups)
            fbgroups_idx['name'][group_name] = newgroup
            fbgroups_idx['id'][group_id] = newgroup
            return newgroup

def add_member_to_group(person,group):
    with db.transaction:
        person.memberof(group)

if __name__ == '__main__' :
    setup_db()

    testgroup = get_or_create_group('testgroup', settings.fb_group_id, 'fb_group')

    user1 = dict(name='User 1',fb_id='test1')
    user2 = dict(name='User 2',fb_id='test2')

    user1['node'] = get_or_create_person(user1)
    user2['node'] = get_or_create_person(user2)

    with db.transaction:
        user1['node'].member_of(testgroup)
        user2['node'].member_of(testgroup)

    db.shutdown()
