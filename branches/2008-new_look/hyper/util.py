# utilities to set up and use the hyper estraier database
import os
import datetime

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

            
    def make_doc(self,hyper_lst):
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
            self.open_w()

        
        for entry in hyper_lst:
            doc = he.Document()
            #for k,v in entry.items():
            #    print "%s: %s" % (k,v,)
            print entry['uri']
            print entry['title']
            print entry['author']
            
            doc.add_attr('@uri',str(entry['uri']).encode('utf-8','ignore'))
            doc.add_attr('@title',entry['title'].encode('utf-8','ignore'))
            doc.add_attr('@author',str(entry['author']).encode('utf-8','ignore'))
            doc.add_attr('@cdate',str(entry['cdate']).encode('utf-8','ignore'))
            doc.add_text(entry['txt'].decode('utf-8','ignore').encode('utf-8','ignore'))
            try:
                doc.add_hidden_text(entry['title'].decode('utf-8','ignore'))
            except Exception,e:
                print str(e)

            if not self.db.put_doc(doc,self.db.PDCLEAN):
                print "put failed"
            else:
                print "put successful"

 
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
            print unicode(e)
            return


    def open_w(self):
        """open db to write"""
        casket = '/var/hyper/casket'
        try:
            db = he.Database()
            db.open(casket,db.DBWRITER | db.DBCREAT)
            self.db = db
        except Exception, e:
            print unicode(e)
            return

    
    def query(self,qs,query_type='SIMPLE'):
        """try query string against the db"""
        self.qs = qs
        try:
            cond = he.Condition()
            cond.set_phrase(qs)
            if query_type == 'SIMPLE':
                qt = cond.SIMPLE
            # results is a list of integers (the ids of the qdbm records)
            results = self.db.search(cond,qt)
            #print results
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


    def print_results(self,docs):
        """
        print the results
        """
        for doc in docs:
            print "<<<--Entry-->>>"
            print "URL: https://collect.rcache.com/detail/%s/" \
                  % doc.attr('@uri') 
            print doc.attr('@title')
            print doc.attr('@cdate')
            print doc.attr('@author')
            print "<<<--Snippet-->>>"
            print self.snippet(doc,self.qs)
            print "<<<--Keywords-->>>"
            print [k for k in self.db.etch_doc(doc, 8)]
            print ""
            print "-"
            print ""
        
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
        log = open('/tmp/hyper.log','w')
        entries = Entry.objects.all()
        hyper_lst = []
        for e in entries:
            try:
                try:
                    author = e.user.id
                except:
                    author = 1
                title = e.entry_name
                uri = e.id
                try:
                    cdate = e.date_created.isoformat()
                except:
                    cdate = datetime.datetime.now().isoformat()
                txt = e.text_content
                d = {'uri':uri,
                     'title':title,
                     'author':author,
                     'cdate':cdate,
                     'txt':txt
                     }
                hyper_lst.append(d)
            except Exception, e:
                print e
                err = str(e) + "\n"
                log.write(err)
                log.flush
                continue
            
            
        self.make_doc(hyper_lst)
        print "Optimizing!!!!!!!!!!!"
        self.optimize_and_close()
        return

    def close(self):
        """
        close the database.
        """
        try:
            self.db.close()
        except:
            pass


        
#-----------------------------------------------------------------------------
# conv. functions
#-----------------------------------------------------------------------------

def load():
    h = HyperUtil()
    h.open_w()
    h.rcache_docs()


def create():
    h = HyperUtil()
    h.create()
    h.close()

    
def search(q):
    h = HyperUtil()
    h.open()
    lst = h.query(q)
    res = h.process_query(lst)
    h.print_results(res)
    #return res
    h.close()

    
if __name__ == '__main__':
    load()
