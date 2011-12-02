import settings
import memberdb
import codecs

dotfile = codecs.open('fbgroup.xml', encoding='utf-8', mode='w+')

memberdb.setupdb()

graph = memberdb.rendergml()

dotfile.write(graph)
