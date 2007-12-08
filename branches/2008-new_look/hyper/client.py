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
    url = 'http://127.0.0.1:1972/node/rcache'
    cond = None
    results = []
    node = None

    def __init__(self,url='http://127.0.0.1:1972/node/rcache'):
        self.url = url
    
    def search(self,query,user_id):
        """
        configure connect and query server -
        returns a list 
        """
        expr = "@author STREQ %s" % user_id
        self.node = h.Node()
        self.node.set_url(self.url)
        self.cond = h.Condition()
        self.cond.set_phrase(query)
        self.cond.add_attr(expr)
        self.results = self.node.search(self.cond, 0)
        return self.results

    def id_lst(self):
        """
        get the list of rcache ids to return for creating a queryset
        """
        lst =[]
        dct = {}
        try:
            for doc in self.results.docs:
                lst.append(doc.attr('@uri'))
                print "adding index to dct: %s" % doc.attr('@uri')
                dct[doc.attr('@uri')] = {'snippet':doc.snippet,
                                         'keywords':self.process_keywords(doc)}
            return lst,dct
        except Exception,e:
            print str(e)
            
            
    def all_attrs(self,uri,user_id):
        """
        get all extra attrs for a uri
        """
        expr_author = "@author STREQ %s" % user_id
        self.node = h.Node()
        self.node.set_url(self.url)
        self.cond = h.Condition()
        self.cond.add_attr(expr_author)
        expr_uri = "@uri STREQ %s" % uri
        self.cond.add_attr(expr_uri)
        results = self.node.search(self.cond, 0)
        the_attrs = {}
        try:
            doc = results.docs[0]
            the_kwords = self.process_keywords(doc)
            the_attrs['kwords'] = the_kwords
            the_attrs['title'] = doc.attr('@title')
            the_attrs['uri'] = doc.attr('@uri')
            the_attrs['he_id'] = doc.attr('@id')
            return the_attrs
        
        except Exception, e:
            print str(e)
            return {}
        
        
    def process_keywords(self,doc):
        raw_kwords = doc.keywords.split("\t")
        the_kwords = []
        i = 0
        kw_count = 0
        for kword in raw_kwords:
            if i == 1:
                i = 0
                continue
            else:
                kw_count += 1
                the_kwords.append(kword)
                i += 1
        #the_kwords.reverse()
        return the_kwords[:8]
