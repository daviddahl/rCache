import md5
import sha
import os
import sys
import re
import urllib

from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.utils import simplejson

import html2text
from twill import get_browser
from twill.commands import go as tw_go
from BeautifulSoup import BeautifulSoup
try:
    if os.environ['RCACHE_USE_TIDY']:
        import tidy
except:
    pass

from rcache.models import *

class LoginError(Exception):
    pass

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
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        e = Entry.objects.filter(user=u).order_by('-id')[:100]
        return render_to_response('recent.html',
                                  {'entries':e,
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

def recent_xhr(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.GET.has_key('offset'):
            e = Entry.objects.filter(user=u).order_by('-id')[:3]
        else:
            if request.GET.has_key('offset'):
                start = int(request.GET['offset']) + 1
                end = start + 20
                e = Entry.objects.filter(user=u).order_by('-id')[start:end]
            else:
                e = Entry.objects.filter(user=u).order_by('-id')[:3]

        json_lst = []
        #cols: id,name,url,date
        for entry in e:
            lst = [entry.id,entry.entry_name,entry.entry_url,
                   entry.date_created.__str__()]
            json_lst.append(lst)
        
        return HttpResponse(simplejson.dumps(json_lst),
                        mimetype='application/javascript')
    else:
        return HttpResponseRedirect("/login_required/")
    
    
def detail(request,entry_id):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        e = Entry.objects.filter(user=u,id__exact=entry_id)
        imgs = Media.objects.filter(entry__exact=e[0])
        links = EntryUrl.objects.filter(entry__exact=e[0])
        tags = Tag.objects.filter(entry__exact=e[0])
        return render_to_response('detail.html',
                                  {'entry':e,
                                   'imgs':imgs,
                                   'links':links,
                                   'tags':tags,
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

    
def spider(request):
    if login_check(request):
        if request.GET.has_key('url'):

            try:
                b = get_browser()
                b.set_agent_string('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)')
                tw_go(request.GET['url'])
                html = b.get_html()
                html_cleaned = toXHTML(html)
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
    else:
        return HttpResponseRedirect("/login_required/")

def new_entry(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        return render_to_response('new_entry.html',
                                  {'user':u})
    else:
        return HttpResponseRedirect("/login_required/")
        

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
    try:
        if request.session['loggedin'] == 1:
            return True
        else:
            return False
    except:
        return False

            
def login(request):
    if request.POST:
        if request.POST.has_key('login'):
            if request.POST.has_key('passwd'):            
                loggedin = authenticate(request.POST['login'],request.POST['passwd'],request.session)
                if loggedin:
                    return HttpResponseRedirect("/recent/")
                else:
                    return HttpResponseRedirect("/login_err/?err=unknown")
            else:
                #error no password
                return HttpResponseRedirect("/login_err/?err=passwd")
        else:
            #error: no username
            return HttpResponseRedirect("/login_err/?err=login")
    else:
        #GET
        return render_to_response('login.html',
                                  {})

def login_err(request):
    error = "Login Incorrect"
    if request.GET['err']:
        if request.GET['err'] == 'passwd':
            error = "Login Failed: Please enter your password."
        if request.GET['err'] == 'login':
            error = "Login Failed: Please enter your login name."
            
    return render_to_response('login_err.html',
                              {'e':error})


def login_required(request):
    return render_to_response('login_required.html',
                              {})
    
def authenticate(login,passwd,session):
    pw_sha = sha.new(unicode(passwd))
    password_enc = pw_sha.hexdigest()
    user = User.objects.filter(login__exact=login,
                               password__exact=password_enc)
    if len(user)==1:
        session['loggedin'] = True
        session['userid'] = user[0].id
        return True
    return False


def logout(request):
    try:
        request.session['loggedin'] = False
        return render_to_response('logout.html',
                                  {})
    except:
        return render_to_response('logout.html',
                                  {})

def postcache(request):
    if login_check(request):
        if request.POST:
            if request.POST['text_content']:
                text_content = urllib.unquote_plus(request.POST['text_content'])
                entry_name = urllib.unquote_plus(request.POST['entry_name'])
                description = urllib.unquote_plus(request.POST['description'])
                entry_url = urllib.unquote_plus(request.POST['entry_url'])
                the_tags = urllib.unquote_plus(request.POST['tags'])
                the_links = urllib.unquote_plus(request.POST['links_qs'])
                the_imgs = urllib.unquote_plus(request.POST['imgs_qs'])
                #print text_content
                print the_links
                print the_imgs
                #fixme: get tags - validate
                tags = manage_tags(the_tags)
                print tags
                #fixme: get links, media
                #create entry object here
                try:
                    #user = User.objects.get(pk=1)
                    _user = User.objects.get(id=request.session['userid'])
                    entry = Entry(text_content=text_content,
                                  entry_name=entry_name,
                                  description=description,
                                  entry_url=entry_url,
                                  user=_user)
                    entry.save()
                    add_tags(tags,_user,entry)
                    entry_urls(the_links,entry,_user)
                    process_media(the_imgs,entry)
                    #fixme: add tags, links, media, etc...
                    print "entry id: %s" % entry.id
                    json_dict=dict(status="success",entry_id=entry.id,
                                   msg="Congrats")
                    return HttpResponse(simplejson.dumps(json_dict),
                                        mimetype='application/javascript')
                except Exception,e:
                    print e
                    json_dict=dict(status="error",entry_id=None,
                                   msg="Something Blew Up!: " + str(e))
                    return HttpResponse(simplejson.dumps(json_dict),
                                        mimetype='application/javascript')
            else:
                json_dict = dict(status="error",msg="No TEXT sent")
                return HttpResponse(simplejson.dumps(json_dict),
                                    mimetype='application/javascript')
        else:
            return HttpResponse(simplejson.dumps(dict(status="error",
                                                      msg="Not POST Method")),
                            mimetype='application/javascript')
    else:
        return HttpResponse(simplejson.dumps(dict(status="error",
                                                  msg="Login Required")),
                            mimetype='application/javascript')


def entry_urls(links,e,u):
    """take links and make EntryUrls..."""
    if links:
        try:
            #break links on '||sep||'
            hrefs = links.split('||sep||')
            for hrf in hrefs:
                if hrf:
                    eu = EntryUrl(url=hrf,entry=e,user=u)
                    eu.save()
        except Exception, e:
            #need to log this:
            print e

def process_media(imgsrcs,e):
    """store url to images scraped from the pages"""
    if imgsrcs:
        try:
            imgs = imgsrcs.split('||sep||')
            for img in imgs:
                if img:
                    m = Media(entry=e,path=img)
                    m.save()
        except Exception,e:
            print e


def update_tags(_user,tags):
    """move this into a utils module to be run by cron every hour..."""
    if tags is not None:
        for tg in tags:
            tc = Tag.objects.filter(user=_user,tag__iexact=tg)
            cnt = len(tc) +1
            for t in tc:
                t.tag_count = cnt
                t.save()
            t = Tag(tag=tg,user=_user,tag_count=cnt)
            

def toXHTML(html):   
    options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0)   
    return tidy.parseString(html, **options)

def login_check_svc(request):
    if login_check(request):
         json_dict = dict(loggedin=1)
    else:
        json_dict = dict(loggedin=0)
    return HttpResponse(simplejson.dumps(json_dict),
                        mimetype='application/javascript')


def add_tags(tags,_user,entry):
    if tags is not None:
        for t in tags:
            texists = Tag.objects.filter(tag__iexact=t,user=_user)
            #fixme: get tag count from join table 
            tagcnt = len(texists)
            if tagcnt == 0:
                tg = Tag(user=_user,tag=t,tag_count=1)
                tg.save()
                entry.tag.add(tg)
            else:
                for existtag in texists:
                    existtag.tag_count = tagcnt
                    existtag.save()
                    entry.tag.add(existtag)

def prune_tags(tags):
    newtags = []
    for t in tags:
        if t == "":
            pass
        else:
            newtags.append(t)
    return newtags
    
    
def manage_tags(tagList):
    if len(tagList)>0:
        if isinstance(tagList,basestring):
            tagList = "," + tagList
            tags = tagList.split(",")
            tags = prune_tags(tags)
            return tags
        elif isinstance(tagList,ListType):
            tags = tagList
            tags = prune_tags(tags)
            return tags
        else:
            return None
    else:
        return None
