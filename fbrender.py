import settings
import memberdb
import codecs

dotfile = codecs.open('fbgroup.dot', encoding='utf-8', mode='w+')

memberdb.setupdb()

graph = memberdb.rendergraph()

dotfile.write(graph)
