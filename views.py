from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.utils import simplejson

import html2text
from twill import get_browser
from twill.commands import go as tw_go
from BeautifulSoup import BeautifulSoup
import tidy

from rcache.models import *

            
def index(request):
    if request.POST:
        post = []
        for (k,v) in request.POST.items():
            post.append(k,v)
    else:
        post = ['GET','No POST']
        
    return render_to_response('index.html',{'p':post})

def bookmarklet(request):
    return render_to_response('bookmarklet.html',dict())

def cache(request):
    if request.GET.has_key('url'):
        #make sure url is properly formatted
        return render_to_response('cache.html',{'u':request.GET['url']})
    else:
        return render_to_response('cache.html',{'u':"Bad Input: No Url Transmitted"})

def recent(request):
    u = User.objects.get(id=1)
    e = Entry.objects.filter(user=u).order_by('-id')[:50]
    return render_to_response('recent.html',
                              {'entries':e})
def detail(request,entry_id):
    u = User.objects.get(id=1)
    e = Entry.objects.filter(user=u,id__exact=entry_id)
    return render_to_response('detail.html',
                              {'entry':e})
def spider(request):
    #check login first
    if request.GET.has_key('url'):

        try:
            b = get_browser()
            b.set_agent_string('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)')
            tw_go(request.GET['url'])
            html = b.get_html()
            #html_cleaned = BeautifulSoup(html)
            html_cleaned = toXHTML(html)
            ## try:
##                 html_cleaned = unicode(html_cleaned)
##             except UnicodeDecodeError,e:
##                 ascii_text = str(html_cleaned).encode('string_escape')
##                 html_cleaned = unicode(ascii_text)

            h,txt = html2text.html2text(html_cleaned.__str__())

            links = b._browser.links()
            _links = []

            code = b.get_code()
            title = b.get_title()
            #insert into database here
            u = User.objects.get(id=1)
            e = Entry(user=u,
                      entry_url=request.GET['url'],
                      entry_name=title,
                      description=title,
                      text_content=txt,
                      html_content=html_cleaned,
                      summary=title)
            e.save()
            #insert entry_urls
            for lnk in links:
                _links.append(lnk.absolute_url)
                eu = EntryUrl(url=lnk.absolute_url,
                              user=u,
                              entry=e)
                eu.save()
            #return dict as JSON
            json_dict =  dict(success=True,
                              url=request.GET['url'],
                              links=_links,
                              code=code,
                              title=title,
                              txt=txt,
                              id=e.id)
        
        except Exception, e:
            json_dict = dict(success=False,
                             error=str(e))
    else:
        json_dict = dict(success=False,
                         error="No Url Provided")
        
        
    return HttpResponse(simplejson.dumps(json_dict),
                        mimetype='application/javascript')


def spider_tags(request):
    #parse tags
    #regex match comma, split on comma
    #if no comma, add the single tag
    #add tags
    #return tags as json list
    tag_list = []
    json_dict=dict(tags=tag_list)
    return HttpResponse(simplejson.dumps(json_dict),
                        mimetype='application/javascript')

def login_check(request):
    #fixme: check for logged in cookie!
    return True

            
def login(request):
    if request.POST.has_key('login'):
        if request.POST.has_key('passwd'):
            ##look up user
            pass
        else:
            #error no password
            pass
    else:
        #error: no username
        pass

def postcache(request):
    if request.POST:
        import urllib
        if request.POST['text_content']:
            text_content = urllib.unquote_plus(request.POST['text_content'])
            entry_name = urllib.unquote_plus(request.POST['entry_name'])
            description = urllib.unquote_plus(request.POST['description'])
            entry_url = urllib.unquote_plus(request.POST['entry_url'])
            print text_content
            #create entry object here
            try:
                user = User.objects.get(pk=1)
                entry = Entry(text_content=text_content,
                              entry_name=entry_name,
                              description=description,
                              entry_url=entry_url,
                              user=user)
                entry.save()
                print "entry id: %s" % entry.id
            except Exception,e:
                print e
            #deal with tags
            
        else:
            json_dict = dict(body="WHOOPS, something blew up")
            
        return HttpResponse(simplejson.dumps(json_dict),
                            mimetype='application/javascript')
    else:
        return HttpResponse(simplejson.dumps(dict(body="Not POST Method")),
                            mimetype='application/javascript')


def toXHTML(html):   
    options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0)   
    return tidy.parseString(html, **options)

