# utilities to set up and use the hyper estraier database
import os
import HyperEstraier as he
from rcache.models import *


class HyperUtil(object):

    casket = None
    db = None
    
    def create(self):
        """ create the casket """
        try:
            #casket = os.environ['HYPERESTRAIER_DB_PATH']
            casket = '/var/hyper/casket'
            db = he.Database()
            db.open(casket,db.DBWRITER | db.DBCREAT)
            self.db = db
            self.casket= casket
        except Exception, e:
            print unicode(e)
            
    def make_doc(self,hyper_lst,txt):
        """Use a dictionary to create a document. the dictionary is like:
        {'@uri': 123,           # my database id
         '@title':u'the title', # title
         '@cdate':'2007/11/12', # creation date
         '@mdate':'2007/11/12', # modification date
         '@adate':'2007/11/13', # access date
         '@author':'The Author',
         '@type':'text/html/xml', # media type
         '@lang': 'en-US',
         '@genre': 'hmmm?',
         '@size': '1024',
         '@weight': 1, # weight as in importance
         '@misc': 'whatever' }
        """
        if not self.db:
            self.open()
            
        for entry in hyper_lst:
            doc = he.Document()
            #for k,v in entry.items():
            #    print "%s: %s" % (k,v,)
            print entry['uri']
            print entry['title']
            print entry['author']
            
            doc.add_attr('@uri',entry['uri'])
            doc.add_attr('@title',entry['title'])
            doc.add_attr('@author',entry['author'])
            
            doc.add_text(txt)

            self.db.put_doc(doc,self.db.PDCLEAN)
        
    def optimize_and_close(self):
        try:
            self.db.optimize(self.db.OPTNODBOPT)
            self.db.close()
        except Exception, e:
            print unicode(e)

    def open(self):
        """open db and add it to instance"""
        #casket = os.environ['HYPERESTRAIER_DB_PATH']
        casket = '/var/hyper/casket'
        try:
            db = he.Database()
            db.open(casket,db.DBREADER | db.DBNOLCK)
            self.db = db
        except Exception, e:
            print uniceod(e)
            return

    def query(self,qs,query_type='SIMPLE'):
        """try query string against the db"""
        try:
            cond = he.Condition()
            cond.set_phrase(qs)
            if query_type == 'SIMPLE':
                qt = cond.SIMPLE
            # results is a list of integers (the ids of the qdbm records)
            results = self.db.search(cond,qt)
            return results
        except Exception, e:
            print unicode(e)
            return []

    def process_query(self,results):
        """
        process results list (integers that are the db ids)
        """
        docs = []
        for res in results:
            docs.append(self.db.get_doc(res,0))
        return docs

    def snippet(self,doc,phrase):
        """
        make a snippet
        """
        return doc.make_snippet([phrase],95,96,96)

    def keywords(self,doc,num_wrds=4):
        """get top keywords in document - returns a list"""
        return self.db.etch_doc(doc,num_wrds)
    
    def rcache_docs(self):
        """
        get all rcache Entries - format as hyper dict
        """
        entries = Entry.objects.all()[:100] # get 100 for now
        hyper_lst = []
        for e in entries:
            print e.entry_name
            d = {'uri': e.id,
                 'title': e.entry_name,
                 'author': e.user.id
                 }
            hyper_lst.append(d)
            
            self.make_doc(hyper_lst,e.text_content)
            
        #self.optimize_and_close()
        return

def load():
    h = HyperUtil()
    h.open()
    h.rcache_docs()

if __name__ == '__main__':
    load()
