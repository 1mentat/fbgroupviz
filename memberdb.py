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

def getmembersgv():
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

def getmembersgml():
    members = unicode("")
    links = unicode("")
    try:
        c.execute("select * from members")
        rows = c.fetchall()
        for row in rows:
            members += unicode("    <node id=\"{0}\"/>\n").format(row[0])
            links += unicode("    <edge source=\"TNE\" target=\"{0}\"/>\n").format(row[0])
    except:
        print "Unexpected error in getmembers():", sys.exc_info()[0], sys.exc_info()[1]
    return members + links

def rendergv() :
    graph = ""
    members = getmembersgv()
    graph += "digraph G {\n"
    graph += members
    graph += "}\n"

    return graph

def rendergml() :
    graph = ""
    members = getmembersgml()
    graph += '''<?xml version="1.0" encoding="UTF-8"?>'''
    graph += '''<graphml xmlns="http://graphml.graphdrawing.org/xmlns"'''
    graph += '''    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'''
    graph += '''    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns'''
    graph += '''    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">'''
    graph += '''<graph id="G" edgedefault="undirected">'''
    graph += members
    graph += '''</graph>'''
    graph += '''</graphml>'''

    return graph

