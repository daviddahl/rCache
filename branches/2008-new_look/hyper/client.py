"""
hyperestraier daemon client
david dahl
2007-11-19
"""
import hyperestraier as h

from rcache.stopwords import stopwords as sw

class HyperClient(object):
    """
    hyperestraier client to wrap hyperestraier pure python module
    """
    def __init__(self,url='http://fisk.rcache.com:1972/node/rcache'):
        self.url = url
        self.init_node()

    def process_stopwords(self,query):
        """
        check query for stopwords! throw them out!
        """
        # tokenize the query:

        new_query = []
        remd_stopwords = []
        query.strip()
        q = query.split(" ")
        for t in q:
            try:
                idx = sw.index(t)
                print 'stop word index: %s, %s' % (str(idx),t)
                remd_stopwords.append(t)
            except Exception,e:
                print str(e)
                new_query.append(t)
        print "len(new_query): %s" % str(len(new_query))
        print "new query: %s" % new_query
        if len(new_query) == 0:                
            removed_stopwords = " ".join(remd_stopwords)
            raise SearchError("Your query cannot be processed after the stopwords are removed: '%s'" % removed_stopwords)

        new_query_str = " ".join(new_query)
        self.new_query_str = new_query_str
        return new_query_str


        
    def search(self,query,user_id):
        """
        configure connect and query server -
        returns a list 
        """
        expr = "@author STREQ %s" % user_id
        self.node.set_url(self.url)
        self.cond = h.Condition()
        q = self.process_stopwords(query)
        print "new query: %s" % q
        self.cond.set_phrase(q)
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
                #print "adding index to dct: %s" % doc.attr('@uri')
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

    
    def doc_add(self,entry):
        """
        Take entry obj, create a new doc and add to the index.
        """
        doc = h.Document()
        doc.add_attr("@uri",str(entry.id))
        doc.add_attr("@title",entry.entry_name)
        doc.add_attr("@author",str(entry.user.id))
        doc.add_text(entry.text_content)
        self.node.put_doc(doc)


    def doc_remove(self,uri):
        """
        get doc via uri, get doc id and remove from index
        """
        id = self.node.uri_to_id(uri)
        doc = self.node.out_doc(id)
        
            
    def doc_update(self,uri,entry):
        """
        do remove and add of entry
        """
        self.doc_remove(uri)
        self.doc_add(entry)


    def init_node(self):
        self.node = h.Node()
        #self.node.set_auth("rcache", "bigrig")
        self.node.set_url(self.url)

class SearchError(Exception):
    """
    raised if query is blank by stopword culling
    """
    pass
