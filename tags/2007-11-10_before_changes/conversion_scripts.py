from rcache.models import *
from urlparse import urlparse

def create_domains():
    ents = Entry.objects.all()
    for e in ents:
        try:
            dom = urlparse(e.entry_url)
            e.entry_domain = dom[1]
            e.save()
            print dom[1]
        except Exception,e:
            print e
