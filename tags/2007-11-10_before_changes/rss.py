import urllib
from rcache.feeds import Feed, add_domain
from rcache.models import *

class LatestEntries(Feed):
    title = "Latest rCache Entries"
    link = "/recent/"
    description = "Your Latest rCache Entries"

    def __init__(self,slug,request):
        #do something with request to get user obj
        self.user = User.objects.get(id=request.session['userid'])
        Feed.__init__(self,slug,request.path)
    
    def items(self):
        return Entry.objects.filter(user=self.user).order_by('-id')[:25]


class LatestEntriesByTag(Feed):
    title = "rCache Entries By Tag"
    link = "/tag/"
    description = "rCache Entries by Tag"

    def __init__(self,slug,request):
        #do something with request to get user obj
        self.user = User.objects.get(id=request.session['userid'])
        if request.GET['tg']:       
            self.tg = urllib.unquote_plus(request.GET['tg'])
        else:
            self.tg=None
        self.description = "rCache Entries by Tag: %s" % self.tg
        self.title = "rCache Entries By Tag: %s" % self.tg  

        Feed.__init__(self,slug,request.path)
    
    def items(self):
        tags = Tag.objects.filter(tag__iexact=self.tg,user=self.user)
        if tags[0]:
            return Entry.objects.filter(tag=tags[0],user=self.user).order_by('-id')[:25]
        else:
            return []
            
            


