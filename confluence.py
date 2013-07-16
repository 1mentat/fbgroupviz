from xmlrpclib import Server

server = 'https://collaboratory.atlassian.net'
space = 'collab'
page = 'Collaboratory Project - Home'

s = Server(server + '/rpc/xmlrpc')
token = s.confluence2.login('jfburns','I2moUp6U')
page = s.confluence2.getPage(token, space, page)

print page['content']

#https://collaboratory.atlassian.net/wiki/display/collab/Collaboratory+Project+-+Home
