import md5
import sha
import os
import sys
import re
import urllib
from urlparse import urlparse

from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.utils import simplejson
from django.core.validators import email_re
from django.core.mail import send_mail

import antiword
import pdf
import html2text
from email_messages import *
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

def contact(request):
    return render_to_response('contact.html',{})

def agreement(request):
    return render_to_response('agreement.html',{})

def privacy(request):
    return render_to_response('privacy.html',{})

def not_found(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        return render_to_response('404.html',
                                  {'user':u})
    else:
        return HttpResponseRedirect("/login_required/")
    
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
        try:
            u = User.objects.get(id=request.session['userid'])
            e = Entry.objects.filter(user=u,id__exact=entry_id)
            imgs = Media.objects.filter(entry__exact=e[0])
            links = EntryUrl.objects.filter(entry__exact=e[0])
            tags = Tag.objects.filter(entry__exact=e[0])
            tags_clean = []
            for t in tags:
                tags_clean.append(t.tag)
            tags_clean = dict.fromkeys(tags_clean).keys()
            return render_to_response('detail.html',
                                      {'entry':e,
                                       'imgs':imgs,
                                       'links':links,
                                       'tags':tags_clean,
                                       'user':u})
        except Exception,e:
            #need to log exception
            #send 404!
            return HttpResponseRedirect("/404/")
    else:
        return HttpResponseRedirect("/login_required/")

def edit_entry(request,entry_id):
    if login_check(request):
        if request.POST:
            #do update here
            #update Entry data
            #get existing tag objects
            #compare existing to POSTED tag list
            #delete tags that are not in POSTED list
            #save tags
            #do the same for links and imgs
            pass
        else:
            try:
                u = User.objects.get(id=request.session['userid'])
                e = Entry.objects.filter(user=u,id__exact=entry_id)
                imgs = Media.objects.filter(entry__exact=e[0])
                links = EntryUrl.objects.filter(entry__exact=e[0])
                tags = Tag.objects.filter(entry__exact=e[0])
                tags_clean = []
                for t in tags:
                    tags_clean.append(t.tag)
                tags_clean = dict.fromkeys(tags_clean).keys()
                entry_tags = ",".join(tags_clean)
                return render_to_response('edit_entry.html',
                                          {'entry':e,
                                           'imgs':imgs,
                                           'links':links,
                                           'tags':tags_clean,
                                           'entry_tags':entry_tags,
                                           'user':u})
            except Exception,e:
                return HttpResponseRedirect("/error/?e=EDIT_ERROR")
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
        if request.POST:
            url = "Manual entry"
            #handle form data
            url = request.POST['url']
            ttl = request.POST['title']
            tgs = request.POST['tags']
            etext = request.POST['entry_text']
            if request.FILES.has_key('the_file'):
                if request.FILES['the_file']:
                    #handle upload
                    file_data = request.FILES['the_file']['content']
                    file_name = request.FILES['the_file']['filename']

                    #if ttl == '':
                    ttl = ttl + ' ** From file: %s ** ' % file_name 

                    content_type = request.FILES['the_file']['content-type']
                    file_txt = '***Error sccraping document: %s ***' % file_name

                    if content_type == 'application/msword':
                        file_txt = process_word(file_data,file_name)
                    elif content_type == 'application/pdf':
                        file_txt = process_pdf(file_data,file_name)
                    #elif content_type == 'text/plain':
                    #    file_txt = process_txt(file_data)
                    else:
                        pass
                etext = etext + "\n------Scraped Text------\n" + file_txt
            if etext:    
                entry = Entry(entry_url=url,
                              entry_name=ttl,
                              text_content=etext,
                              user=u)
                entry.save()
                #handle tags here!
                taglist = manage_tags(tgs)
                add_tags(taglist,u,entry)
                detail_url = "/detail/%s/" % entry.id
                return HttpResponseRedirect(detail_url)
            else:
                m="Please upload a file or enter some Entry Text."
                return render_to_response('new_entry.html',
                                          {'user':u,
                                           'message':m})
        else:            
            return render_to_response('new_entry.html',
                                      {'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

def search(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        
        if request.POST:
            if request.POST['search_str']:
                params = request.POST['search_str']
                
                #entries = Entry.objects.filter(text_content__search=params)
                e = Entry()
                entries = e.fulltxt(u,params)
                return render_to_response('search_results.html',
                                          {'user':u,
                                           'params':params,
                                           'entries':entries})
            else:
                return render_to_response('search.html',
                                          {'user':u,
                                           'errormsg':True
                                           })
        else:
            return render_to_response('search.html',
                                      {'user':u})
    else:
        return HttpResponseRedirect("/login_required/")


def firefox(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        
        return render_to_response('firefox.html',
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

def loginxul(request):
    loggedin = False
    request.session['loggedin'] = False
    if request.POST:
        loggedin = authenticate(request.POST['login'],request.POST['passwd'],request.session)
        if loggedin:
            message = 'Success'
        else:
            message = 'Login Failed'
    else:
        message = None
    return render_to_response('loginxul.html',
                              {'logged_in':loggedin,
                               'message':message})
    
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
                try:
                    parsed_url = urlparse(entry_url)
                    edomain = parsed_url[1]
                except:
                    edomain = ""
                    
                tags = manage_tags(the_tags)
                try:
                    _user = User.objects.get(id=request.session['userid'])
                    entry = Entry(text_content=text_content,
                                  entry_name=entry_name,
                                  description=description,
                                  entry_url=entry_url,
                                  user=_user,
                                  entry_domain=edomain)
                    entry.save()
                    add_tags(tags,_user,entry)
                    entry_urls(the_links,entry,_user)
                    process_media(the_imgs,entry)

                    return HttpResponse(simplejson.dumps('done'),
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
        #dict(status="error",msg="Login Required: In your browser, go to https://rcache.com/login/")
        return HttpResponse(simplejson.dumps('login_error'),
                            mimetype='application/javascript')

def remove_entry(request,entry_id):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        entry = Entry.objects.filter(id=entry_id,user=u)
        if len(entry) == 1:
            e = entry[0]
            return render_to_response('remove_entry.html',
                                      {'entry':e,
                                       'user':u})
        else:
            #error! too many objects found or no objects found
                return HttpResponseRedirect("/error/?e=UNKNOWN")
    else:
        #not logged in
        return HttpResponseRedirect("/login_required/")

def removeit(request,entry_id):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        entry = Entry.objects.filter(id=entry_id,user=u)
        if len(entry) == 1:
            title = entry[0].entry_name
            entry[0].delete()
            
            return render_to_response('removed.html',
                                      {'entry_name':title,
                                       'user':u})
        else:
            #error! too many objects found or no objects found
                return HttpResponseRedirect("/error/?e=ERR_REMOVE_ENTRY")
    else:
        #not logged in
        return HttpResponseRedirect("/login_required/")

def err_unknown(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.GET.has_key('e'):
            err = request.GET['e']
        else:
            err = 'Unknown'
        return render_to_response('err_unknown.html',
                                  {'err':err,
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

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
            texists = Tag.objects.filter(tag__iexact=t,user=_user).order_by('id')
            #tagcnt = len(texists)
            tagcnt = tag_count_recurse(t,_user)
            if tagcnt == 0:
                tg = Tag(user=_user,tag=t,tag_count=1)
                tg.save()
                entry.tag.add(tg)
            else:
                for existtag in texists:
                    existtag.tag_count = tagcnt
                    existtag.save()
                    entry.tag.add(existtag)

def tag_count_recurse(tag,_user):
    texists = Tag.objects.filter(tag__iexact=tag,user=_user).order_by('id')
    tcount = 0
    if len(texists)> 0:
        for tg in texists:
            tcount += tg.tag_count
    return tcount
            

def prune_tags(tags):
    newtags = []
    for t in tags:
        if t == "":
            pass
        else:
            tag = t.strip()
            newtags.append(tag)
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

#fixme: need to write these functions and supporting classes/modules

def upload(request):
    """handle uploaded file no bigger than $threshold"""
    pass

def process_word(data,filename):
    """pass word doc through antiword, save output text to entry, save original file in database"""
    tmp_name = antiword.save_tmp(data)
    try:
        the_text = antiword.extractText(tmp_name)
        return the_text
    except:
        return "Error processing Word doc: %s" % filename

def process_pdf(data,filename):
    """scrape text from PDF, store as an entry and Media record"""
    tmp_name = pdf.save_tmp(data)
    try:
        the_text = pdf.extractPDFText(tmp_name)
        return the_text
    except:
        return "Error processing PDF file: %s" % filename
    

def search_engine(request):
    """pass search request to database fulltext query or Nutch or PyLucene, not sure which one yet."""
    pass

def tag(request):
    """filter entries by tag"""
    if login_check(request):
        #try:
        if request.GET['tg']:
            u = User.objects.get(id=request.session['userid'])
            tg = urllib.unquote_plus(request.GET['tg'])
            #search user's records for all entrys that have this tag:
            tags = Tag.objects.filter(tag__iexact=tg,user=u)
            entries = []
            #fixme: duplicate entries are added to theis list!
            for t in tags:
                e = Entry.objects.filter(tag=t,user=u).order_by('-id')
                entries.extend(e)
            return render_to_response('tag_results.html',
                                      {'user':u,
                                       'the_tag':tg,
                                       'entries':entries})
        #except Exception,e:

        #    return HttpResponseRedirect("/404/")
        else:
            return HttpResponseRedirect("/404/")
    else:
        return HttpResponseRedirect("/login_required/")

    
def tag_list(request):
    """get most popular tags by user"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        t = Tag()
        if request.GET.has_key('op'):
            if request.GET['op'] == 'all':
                tags = t.tag_list(u,which_q='all')
            elif request.GET['op'] == 'alpha':
                tags = t.tag_list(u,which_q='alpha')
            else:
                tags = t.tag_list(u)
        else:
            tags = t.tag_list(u)
        return render_to_response('tag_list.html',
                                  {'user':u,
                                   'tags':tags})
    else:
        return HttpResponseRedirect("/login_required/")

def domain_list(request):
    """get domains alphabetically for domain list"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        e = Entry()
        
        domains = e.domain_list(u)
        return render_to_response('domain_list.html',
                                  {'user':u,
                                   'domains':domains})
    else:
        return HttpResponseRedirect("/login_required/")

def domain_filter(request):
    """filter entries by domain"""
    if login_check(request):
        #try:
        if request.GET['domain']:
            u = User.objects.get(id=request.session['userid'])
            tg = urllib.unquote_plus(request.GET['domain'])
            #search user's records for all entrys that were scraped from this domain

            entries = Entry.objects.filter(entry_domain__iexact=request.GET['domain'],user=u)
            
            return render_to_response('domain_results.html',
                                      {'user':u,
                                       'the_domain':request.GET['domain'],
                                       'entries':entries})
        #except Exception,e:

        #    return HttpResponseRedirect("/404/")
        else:
            return HttpResponseRedirect("/404/")
    else:
        return HttpResponseRedirect("/login_required/")

def account_new(request):
    """Create new account"""
    m = None
    if request.POST:
        if request.POST['email']:
            try:
                if email_re.search(request.POST['email']):
                    comp = Company.objects.get(pk=1)
                    u = User(email=request.POST['email'],
                             company=comp,login=request.POST['email'])
                    u.save()

                    m = ""
                    #send email
                    msg = message_new_account % (u.email,
                                                 request.POST['research_type'],)
                    send_mail('rCache Account Application',
                              msg,
                              'admin@rcache.com',
                              [u.email,'admin@rcache.com',],
                              fail_silently=False)
                    return render_to_response('account_pending.html',{'message':m})
                else:
                    m = "Email address is not valid."
                return render_to_response('account.html',{'message':m})
                
            except Exception,e:
                m = "An error occurred creating an account for %s. Please send an email to admin at rcache dot com, please include this error message" % request.POST['email']
                return render_to_response('account.html',{'message':m})
        else:
            m = "Please Enter your email address"
            return render_to_response('account.html',{'message':m})
    else:
        return render_to_response('account.html',{'message':m})


def myaccount(request):
  """Tweak existing account"""
  if login_check(request):
      u = User.objects.get(id=request.session['userid'])
      if request.POST:
          err = []
          if request.POST['password'] and request.POST['password_conf']:
              if request.POST['password'] == request.POST['password_conf']:
                  pw_sha = sha.new(unicode(request.POST['password']))
                  password_enc = pw_sha.hexdigest()
                  u.password = password_enc
              else:
                  #passwords do not match
                  err.append("Password and Password Confirm do not match.")
                  render_to_response('myaccount.html',{'user':u,
                                                       'err':err})
          if request.POST['email']:
              try:
                  if isValidEmail(request.POST['email'],None):
                      u.email = request.POST['email']
              except:
                  err.append("Email Address is not valid.")
                  render_to_response('myaccount.html',{'user':u,
                                                         'err':err})
              u.blogurl = request.POST['blogurl']
              u.website = request.POST['website']
              u.first_name = request.POST['first_name']
              u.first_name = request.POST['last_name']
              if u.email == 'demo@rcache.com':
                  #do not allow updates to demo account!
                  pass
              else:
                  u.save()
              return render_to_response('myaccount.html',{'user':u})
          else:
              #email required
              pass
      else:
          return render_to_response('myaccount.html',{'user':u})
  else:
      return HttpResponseRedirect("/login_required/")

def about(request):
    return render_to_response('about.html',{})

def approve_user(user_id,passwd):
    try:
        u = User.objects.get(pk=user_id)
        pw_sha = sha.new(unicode(passwd))
        password_enc = pw_sha.hexdigest()
        u.password = password_enc
        u.active = 1
        u.save()
        print "User %s password created!" % u.login
    except Exception, e:
        print e
    
