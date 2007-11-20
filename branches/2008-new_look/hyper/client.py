"""
hyperestraier daemon client
david dahl
2007-11-19
"""

import hyperestraier as h

class HyperClient(object):
    """
    hyperestraier client to wrap hyperestraier pure python module
    """
    url = 'http://127.0.0.1:1978/node/rcache'
    cond = None
    results = []
    node = None

    def __init__(self,url='http://127.0.0.1:1978/node/rcache'):
        self.url = url
    
    def search(self,query):
        """
        configure connect and query server -
        returns a list 
        """
        self.node = h.Node()
        self.node.set_url(self.url)
        self.cond = h.Condition()
        self.cond.set_phrase(query)
        self.results = self.node.search(self.cond, 0)
        return self.results

    def id_lst(self):
        """
        get the list of rcache ids to return for creating a queryset
        """
        lst =[]
        try:
            for doc in self.results.docs:
                lst.append(doc.attr('@uri'))
            return lst
        except Exception,e:
            print str(e)
            
            
            

