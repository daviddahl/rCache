import datetime
import hyperestraier

from client import HyperClient as hc
from rcache.stopwords import stopwords as sw
from rcache.models import Document


def load():
    """
    load the rcache database into a newly-minted hyperestraier node
    """
    h = hc(url='http://127.0.0.1:1972/node/rcache')
    docs = Document.objects.all()
    for doc in docs:
        try:
            h.doc_add(doc)
            print "loaded entry # %s" % doc.id 
        except Exception, e:
            print "Could not load entry into HyperEstraier"
            print e
