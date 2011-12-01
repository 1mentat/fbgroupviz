import sqlite3
import sys
import datetime

conn = None
c = None

def setupdb() :
    global conn
    global c

    conn = sqlite3.connect('fbgroup.db')

    c = conn.cursor()

    try:
        c.execute('''create table if not exists members (id integer, name text, url text, unique(id))''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create members"

    try:
        c.execute('''create table if not exists links (sid integer, tid integer, unique(sid,tid))''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create links"

    return 0

def addmember(id, name, url):
    try:
        c.execute("insert or ignore into members values (?, ?, ?)", (int(id),name,url))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on member insert"

def addlink(sid, tid):
    try:
        c.execute("insert into links values (?, ?)", (sid,tid))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on link insert"

def getmembers():
    members = unicode("")
    links = unicode("")
    try:
        c.execute("select * from members")
        rows = c.fetchall()
        for row in rows:
            members += unicode("    {0} [label=\"{1}\", href=\"{2}\"]\n").format(row[0],row[1],row[2])
            links += unicode("    TNE -> {0}\n").format(row[0])
    except:
        print "Unexpected error in getmembers():", sys.exc_info()[0], sys.exc_info()[1]
    return members + links

def rendergraph() :
    graph = ""
    members = getmembers()
    graph += "digraph G {\n"
    graph += members
    graph += "}\n"

    return graph

