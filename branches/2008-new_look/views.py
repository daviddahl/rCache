import md5
import sha
import os
import sys
import re
import urllib
import copy
import time
from urlparse import urlparse
from cgi import escape

from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _
from django.core.validators import email_re
from django.core.mail import send_mail
from django.contrib.syndication import feeds
from django import newforms as forms

from account.views import hash_key
import antiword
import pdf
import html2text
from email_messages import *
try:
    from twill import get_browser
    from twill.commands import go as tw_go
except:
    tw_go = None
#from BeautifulSoup import BeautifulSoup
try:
    if os.environ['RCACHE_USE_TIDY']:
        import tidy
except:
    pass

from rcache.models import *
from rcache.forms import *
from rcache.settings import *
from rcache.hyper.client import HyperClient

search_refer = re.compile("/search/$")

class LoginError(Exception):
    pass

def index(request):
    return render_to_response('index.html',{})

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
        return render_to_response('404logged_in.html',
                                  {'user':u})
    else:
        return render_to_response('404.html',
                                  {'user':None})


def colleagues(request):
    """find existing colleagues, display options to create a new colleague
    and edit coll. privs"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        c = Colleague.objects.filter(user_id__exact=request.session['userid']).order_by('-id')
        
        return render_to_response('colleagues.html',
                                  {'colleagues':c,
                                   'colleagues_cnt':len(c),
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

def colleague_detail(request,coll_id):
    """edit colleague's detail data"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.POST:
            POST = request.POST
            try:
                #get collague
                c = Colleague.objects.filter(id=coll_id,user_id=u.id)
                print c[0]
                coll = c[0]
                #validate posted colleague data
                if POST.has_key("active"):
                    coll.active = True
                else:
                    coll.active = False
                if POST.has_key("search_restrictions"):
                    coll.search_restrictions = True
                else:
                    coll.search_restrictions = False
                if POST.has_key("tag_restrictions"):
                    coll.tag_restrictions = True
                else:
                    coll.tag_restrictions = False
                if POST.has_key("search_keywords_approved"):
                    coll.search_keywords_approved = POST["search_keywords_approved"]
                if POST.has_key("tags_approved"):
                    coll.tags_approved = POST["tags_approved"]
                if POST.has_key("commentary"):
                    coll.commentary = True
                else:
                    coll.commentary = False
                coll.save()
                #return HttpResponseRedirect("/colleague/%s/?updated" % coll.id)
                return render_to_response('colleague_detail.html',
                                          {'user':u,
                                           'colleague':coll,
                                           'updated':True})
            except Exception,e:
                m= _("Error: Cannot Update Colleague. %s") % e
                return render_to_response('colleague_err.html',
                                          {'user':u,
                                           'message':m})
            
        else:
            try:
                c = Colleague.objects.filter(id__exact=coll_id,user_id=request.session['userid'])
                return render_to_response('colleague_detail.html',
                                          {'colleague':c[0],
                                           'user':u})
            except Exception,e:
                m= _("Error: Cannot fetch Colleague record. Perhaps your Colleague has not accepted the account offer")
                return render_to_response('colleague_err.html',
                                          {'user':u,
                                           'message':m})
    else:
        return HttpResponseRedirect("/login_required/")


def new_colleague(request):
    """create a new colleague object"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.POST:
            #check if you are adding the same coll. twice
            cols = Colleague.objects.filter(user_id__exact=u.id)
            for col in cols:
                if col.colleague.login == request.POST["colleague_email"]:
                    #err: need to return with "you already have that colleague"
                    m = _("That email address is already used by one of your colleagues.")
                    return render_to_response('new_colleague.html',
                                              {'user':u,
                                               'message':m,
                                               'posted':request.POST})
            #validate posted data...
            valid = validate_new_colleague(request.POST)
            if valid is not None:
                #valid!
                #fixme: try...
                #create User object
                comp = Company.objects.get(pk=1)
                coll_user,created = \
                                  User.objects.get_or_create(email=valid['email'],
                                                             company=comp,
                                                             login=valid['email'])
                coll_user.save()
                
                #create colleague object
                coll = Colleague(colleague=coll_user,
                                 user_id=request.session['userid'],
                                 active=valid['active'],
                                 tag_restrictions=valid['tag_restrictions'],
                                 tags_approved=valid['tags_approved'],
                                 search_restrictions=valid['search_restrictions'],
                                 search_keywords_approved=valid['search_keywords_approved'],
                                 commentary=valid['commentary'])

                coll.save()
                
                #create colleage for coll_user
                new_user_coll = Colleague(colleague=u,
                                 user_id=coll_user.id,
                                 active=True,
                                 tag_restrictions=True,
                                 tags_approved="",
                                 search_restrictions=True,
                                 search_keywords_approved="",
                                 commentary=False)
                new_user_coll.save()
                
                #create hash_key:
                hk = hash_key(u)
                evt_invite = UserEvent(user=u,
                                       hash_key=hk,
                                       event_type='Invite Colleague')
                evt_invite.save()
                
                hk2 = hash_key(coll_user)
                evt_invited = UserEvent(user=coll_user,
                                        hash_key=hk2,
                                        event_type='Invited Colleague')
                evt_invited.save()
                
                subject = _("rCache.com: Collaborative Research Request")
                if created:
                    mesg = _("""Dear %(user_email)s,\n\nYour colleague, %(col_email)s, would like to share some research with you via rcache.com, a collaborative online research tool. you can read about rcache's functionality here: http://www.rcache.com/about/.\n\nIf you would like to accept %(user_email)s's offer to become an online rCache colleague, click here: https://collect.rcache.com/accounts/activate/?hk=%(hash_key)s\n\nYou will be granted a full rCache account (if you do not already have one) which you can use to collect and store data from the web and elsewhere. rCache is free and easy to use.\n\nBest Regards,\n\nrCache Account Bot""") % \
                           {'col_email':coll_user.email,
                            'user_email':u.email,
                            'hash_key':hk2}
                else:
                    mesg = _("""Dear %(coll_user)s,\n\nYour colleague, %(user_email)s, would like to share some research with you via your rcache.com account.\n\nClick here to login and configure your Colleague settings: https://collect.rcache.com/login/\n\nBest Regards,\n\nrCache Account Bot""") %\
                           {'coll_user':coll_user.email,
                            'user_email':u.email}
                
                send_mail(subject,
                          mesg,
                          'admin@rcache.com',
                          [coll_user.email,'admin@rcache.com',],
                          fail_silently=True,auth_user=EMAIL_HOST_USER,
                          auth_password=EMAIL_HOST_PASSWORD)
                m = ""
                c = Colleague.objects.filter(user_id__exact=request.session['userid']).order_by("-id")
                return render_to_response('colleague_pending.html',
                                          {'message':m,
                                           'user':u,
                                           'colleagues':c,
                                           'colleagues_cnt':len(c)})
            else:
                m = _("Please make sure the email address is correct, and you have entered the email in 'Confirm Email'")
                return render_to_response('new_colleague.html',
                                          {'user':u,
                                           'message':m,
                                           'posted':request.POST})
        else:
            return render_to_response('new_colleague.html',
                                      {'user':u})
    
    else:
        return HttpResponseRedirect("/login_required/")

def validate_new_colleague(POST):
    #create a default set of restrictons... pretty open
    active = True
    search_restrictions = False
    tag_restrictions = False
    search_keywords_approved = ""
    tags_approved = ""
    commentary = False
    if POST.has_key("colleague_email") and \
           POST.has_key("colleague_email_conf"):
        if POST["colleague_email"] == POST["colleague_email_conf"] and \
               email_re.search(POST['colleague_email']):
            #need to lookup this email to see if the
            #colleague is a user already for this user
            
            if POST.has_key("active"):
                active = True
            if POST.has_key("search_restrictions"):
                search_restrictions = True
            if POST.has_key("tag_restrictions"):
                tag_restrictions = True
            if POST.has_key("search_keywords_approved"):
                search_keywords_approved = POST["search_keywords_approved"]
            if POST.has_key("tags_approved"):
                tags_approved = POST["tags_approved"]
            if POST.has_key("commentary"):
                commentary = True
                
            coll_dict = {'email':POST["colleague_email"],
                         'active':active,
                         'search_restrictions':search_restrictions,
                         'tag_restrictions':tag_restrictions,
                         'search_keywords_approved':search_keywords_approved,
                         'tags_approved':tags_approved,
                         'commentary':commentary}
            return coll_dict
        else:
            return None
    else:
        return None

def colleague_research(request,coll_id):
    """View your colleague's research if they have given you access..."""
    """need to load up all tags and search keywords into a dictionary with
    2 lists. one for tags one for keywords.
    before issuing one of these searches, check the session for the
    keyword or tag, then issue the search. reload them each time you hit
    a colleague research detail screen. The dict will be like this:

    coll_research = [{ colleague_user_id:id,
                      tags:[foo,bar,baz,],
                      kw:[foo,bar,baz,]},]

    """
    if login_check(request):
        try:
            u = User.objects.get(id=request.session['userid'])
            #current user is the colleague, user_id is owner of colleague
            c = Colleague.objects.filter(user_id=coll_id,colleague=u)
            colleague = User.objects.get(id=coll_id)

            if c[0].active:
                active_txt = _("Active")
            else:
                active_txt = _("Not Active")
                m = _("Your Colleague Status with %(col_login)s is Inactive.") \
                      % {'col_login':colleague.login}
                return render_to_response('colleague_err.html',
                                          {'user':u,
                                           'err':True,
                                           'message':m})
        except Exception,e:
            m = _("Colleague Not Found.")
            return render_to_response('colleague_err.html',
                                      {'user':u,
                                       'err':True,
                                       'message':m})
            
        if c[0].tag_restrictions and \
           c[0].search_restrictions and \
           c[0].tags_approved == "" and \
           c[0].search_keywords_approved == "":
            initial_state_txt = _("Your colleague account with %(col_login)s has not been configured yet") % {'col_login':colleague.login}
        else:
            initial_state_txt = None

        tgs = manage_tags(c[0].tags_approved)
        srch = manage_tags(c[0].search_keywords_approved)
        
        return render_to_response('colleague_research.html',
                                  {'user_colleague_record':c[0],
                                   'colleague':colleague,
                                   'user':u,
                                   'active_txt':active_txt,
                                   'initial_state_txt':initial_state_txt,
                                   'tags':tgs,
                                   'search_kw':srch,
                                   'err':None})

        ## m = "You are not listed as a colleague, or they may have just revoked your privileges."
##         return render_to_response('colleague_research.html',
##                                   {'colleague':None,
##                                    'user':u,
##                                    'err':True})
    else:
        return HttpResponseRedirect("/login_required/")

def colleague_research_tag(request,coll_id):
    """use colleague's tag to do a tagsearch on their entries"""
    if login_check(request):
        try:
            u = User.objects.get(id=request.session['userid'])
            c = Colleague.objects.filter(user_id=coll_id,colleague=u)
            colleague = User.objects.get(id=coll_id)
            can_search = colleague_check(request,coll_id)

            if can_search is True:
                tg = urllib.unquote_plus(request.GET['tag'])
                tags = Tag.objects.filter(tag__iexact=tg,user=colleague)
                entries = []
                #fixme: duplicate entries are added to this list!
                for t in tags:
                    e = Entry.objects.filter(tag=t,user=colleague).order_by('-id')
                    entries.extend(e)
                
                back_lnk = "/colleague/%s/research/" % coll_id
                return render_to_response('tag_results.html',
                                          {'user':u,
                                           'the_tag':tg,
                                           'entries':entries,
                                           'coll_id':coll_id,
                                           'coll_login':colleague.login,
                                           'back_lnk':back_lnk,
                                           'coll_render':True})
            else:
                #return error message
                m= _("You do not have permission to search %(col_login)s's entries tagged: %(tag)s") %\
                   {'col_login':colleague.login,
                    'tag':urllib.unquote_plus(request.GET['tag'])}
                return render_to_response('colleague_err.html',
                                          {'user':u,
                                           'err':True,
                                           'message':m})
        except Exception,e:
            m= _("An error occurred trying to lookup your colleague's research. %s") % e
            return render_to_response('colleague_err.html',
                                      {'user':u,
                                       'err':True,
                                       'message':m})
    else:
        return HttpResponseRedirect("/login_required/")
    
def colleague_research_keywords(request,coll_id):
    """allow searching of colleague's entries via a list of keywords"""
    if login_check(request):
        try:
            u = User.objects.get(id=request.session['userid'])
            c = Colleague.objects.filter(user_id=coll_id,colleague=u)
            colleague = User.objects.get(id=coll_id)
            can_search = colleague_check(request,coll_id,query_type="search")

            if can_search is True:
                kw = urllib.unquote_plus(request.GET['kw'])
                e = Entry()
                entries = e.fulltxt(colleague,kw)
                
                back_lnk = "/colleague/%s/research/" % coll_id
                return render_to_response('search_results.html',
                                          {'user':u,
                                           'the_kw':kw,
                                           'entries':entries,
                                           'coll_id':coll_id,
                                           'coll_login':colleague.login,
                                           'back_lnk':back_lnk,
                                           'coll_render':True})
            else:
                #return error message
                m= _("You do not have permission to search %(col_login)s's entries with the keyword: %(kword)s") %\
                   {'col_login':colleague.login,
                    'kword':urllib.unquote_plus(request.GET['search'])}
                return render_to_response('colleague_err.html',
                                          {'user':u,
                                           'err':True,
                                           'message':m})
        except Exception,e:
            m= _("An error occurred trying to lookup your colleague's research. %(err)s") % {'err':e}
            return render_to_response('colleague_err.html',
                                      {'user':u,
                                       'err':True,
                                       'message':m})
    else:
        return HttpResponseRedirect("/login_required/")


def colleague_check(request,coll_id,query_type="tag"):
    """check if colleague is your colleague and you can do the search that is attempted"""
    print "query_type %s" % query_type
    u = User.objects.get(id=request.session['userid'])
    #current user is the colleague, user_id is owner of colleague
    c = Colleague.objects.filter(user_id=coll_id,colleague=u)
    colleague = User.objects.get(id=coll_id)
    
    if c[0].active:
        active_txt = _("Active")
    else:
        active_txt = _("Not Active")
        
    if c[0].tag_restrictions and \
           c[0].search_restrictions and \
           c[0].tags_approved == "" and \
           c[0].search_keywords_approved == "":
        initial_state_txt = _("Your colleague account with %(col_login)s has not been configured yet") % {'col_login':colleague.login}
        #return error as you do not have access yet
        return False
    else:
        initial_state_txt = None
        
    tgs = manage_tags(c[0].tags_approved)
    srch = manage_tags(c[0].search_keywords_approved)

    if query_type == 'tag':
        the_tag = urllib.unquote_plus(request.GET['tag']).lower()
        if tgs.index(the_tag) > -1:
            return True
        else:
            return False
    elif query_type == 'search':
        try:
            the_kw = urllib.unquote_plus(request.GET['kw']).lower()
        except:
            the_kw = urllib.unquote_plus(request.GET['search']).lower()
        if srch.index(the_kw) > -1:
            return True
        else:
            return False
    else:
        return False

def colleague_check_detail(request,coll_id,query_type):
    """lookup colleague's entry - check either it's tags or
    keywords against colleague record"""
    try:
        coll_chk = colleague_check(request,coll_id,query_type=query_type)
    except Exception,e:
        return False
    if coll_chk is True:
        return True
    else:
        return False
        
def internal_request(domain,referer):
    return referer is not None and re.match("^https?://%s/" % re.escape(domain), referer)
    
def colleague_research_detail(request,coll_id,entry_id):
    """Display entry detail for an entry compiled by a colleague"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.GET.has_key('search'):
            query_type = 'search'
        elif request.GET.has_key('tag'):
            query_type = 'tag'
        else:
            m = _("Error fetching entry. Could not determine Query Type.")
            return render_to_response('colleague_err.html',
                                      {'user':u,
                                       'err':True,
                                       'message':m})
        
        if colleague_check_detail(request,coll_id,query_type):
            #so far so good
            colleague = User.objects.get(id=coll_id)
            print colleague
            e = Entry.objects.filter(user=colleague,id__exact=entry_id)
            escaped_text_content = escape(e[0].text_content)
            imgs = Media.objects.filter(entry__exact=e[0])
            links = EntryUrl.objects.filter(entry__exact=e[0])
            tags = Tag.objects.filter(entry__exact=e[0])
            tags_clean = []
            for t in tags:
                tags_clean.append(t.tag)
            tags_clean = dict.fromkeys(tags_clean).keys()

            from django import http
            domain = http.get_host(request)
            referer = request.META.get('HTTP_REFERER', None)
            is_internal = internal_request(domain, referer)
            if is_internal:
                back_lnk = referer
            else:
                back_lnk = None
                
            if search_refer.search(referer):
                back_lnk = None
                    
            return render_to_response('detail.html',
                                      {'entry':e,
                                       'imgs':imgs,
                                       'links':links,
                                       'tags':tags_clean,
                                       'user':u,
                                       'colleague':colleague,
                                       'coll_render':True,
                                       'back_lnk':back_lnk,
                                       'escaped_text_content':escaped_text_content})
        else:
            m = _("Error fetching entry. Could not determine Query Type.")
            return render_to_response('colleague_err.html',
                                      {'user':u,
                                       'err':True,
                                       'message':m})
            
    else:
        return HttpResponseRedirect("/login_required/")
    
def recent(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        e = Entry.objects.filter(user=u).order_by('-id')[:50]
        #request.session['back_lnk'] = 
        return render_to_response('recent.html',
                                  {'entries':e,
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

def recent_original(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        e = Entry.objects.filter(user=u).order_by('-id')[:50]
        #request.session['back_lnk'] = 
        return render_to_response('recent_orig.html',
                                  {'entries':e,
                                   'user':u})
    else:
        return HttpResponseRedirect("/login_required/")

def recent_xhr(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.GET.has_key('offset'):
            e = Entry.objects.filter(user=u).order_by('-id')[:200]
        else:
            if request.GET.has_key('offset'):
                start = int(request.GET['offset']) + 1
                end = start + 25
                e = Entry.objects.filter(user=u).order_by('-id')[start:end]
            else:
                e = Entry.objects.filter(user=u).order_by('-id')[:200]
        json_lst = []
        #cols: id,name,url,date
        json_dct = {'entries_db':
                    {'totalItems':len(e),
                     'itemsFound':len(e),
                     'items':[]
                     }
                    }
        for entry in e:
            #url = '<a href="%s" target="_new">Go</a>' % entry.entry_url
            e_lst = entry.entry_name.split(' ')[:10]
            e_str = " ".join(e_lst)
            detail_link = '<a href="/detail/%s/">%s</a>' % \
                          (entry.id,e_str,)
            dct = {
                   'rcacheid':entry.id,
                   'name':e_str,
                   #'url':url,
                   'date':entry.date_created.__str__()}
            json_dct['entries_db']['items'].append(dct)
            
        return HttpResponse(simplejson.dumps(json_dct),
                        mimetype='application/javascript')
    else:
        return HttpResponseRedirect("/login_required/")
    
    
def detail(request,entry_id):
    if login_check(request):
        entry_attrs = []
        kwords_for_query = []
        try:
            u = User.objects.get(id=request.session['userid'])
            e = Entry.objects.filter(user=u,id__exact=entry_id)[0]
            try:
                h = HyperClient(url=os.environ['RCACHE_HYPER_URL'])
                entry_attrs = h.all_attrs(str(e.id),u.id)
                try:
                   kw_for_q = entry_attrs['kwords']
                   kwords_for_query = " ".join(kw_for_q)
                except Exception, ex:
                    print ex
            except Exception, ex:
                print ex
                entry_attrs = {}
            
            escaped_text_content = escape(e.text_content)
            imgs = Media.objects.filter(entry__exact=e)
            links = EntryUrl.objects.filter(entry__exact=e)
            tags = Tag.objects.filter(entry__exact=e)
            tags_clean = []
            for t in tags:
                tags_clean.append(t.tag)
            tags_clean = dict.fromkeys(tags_clean).keys()
            links_len = len(links)
            imgs_len = len(imgs)
            if imgs_len == 0 or links_len == 0:
                 entry_txt_id = 'detail_entry_text_long'
            else:
                entry_txt_id = 'detail_entry_text'

            from django import http
            domain = http.get_host(request)
            referer = request.META.get('HTTP_REFERER', None)
            is_internal = internal_request(domain, referer)
            if is_internal:
                back_lnk = None
                
            else:
                back_lnk = None    
            if request.GET.has_key('recent_enhanced'):
                recent_enhanced = True
            else:
                recent_enhanced = False
                
            return render_to_response('detail.html',
                                      {'entry':e,
                                       'escaped_text_content':escaped_text_content,
                                       'imgs':imgs,
                                       'links':links,
                                       'links_len':links_len,
                                       'tags':tags_clean,
                                       'imgs_len':imgs_len,
                                       'entry_txt_id':entry_txt_id,
                                       'edit_buttons':True,
                                       'back_lnk':back_lnk,
                                       'user':u,
                                       'recent_enhanced':recent_enhanced,
                                       'entry_attrs':entry_attrs,
                                       'kwords_for_query':kwords_for_query})
        except Exception,e:
            #need to log exception
            #send 404!
            return HttpResponseRedirect("/404/")
    else:
        return HttpResponseRedirect("/login_required/")

def entry_validate(POST):
    try:
        if POST['text_content']:
            return True
        else:
            return False
    except:
        return False

def edit_entry(request,entry_id):
    if login_check(request):
        if request.POST:
            if entry_validate(request.POST):
                
                u = User.objects.get(id=request.session['userid'])
                #do update here
                #update Entry data
                etry = Entry.objects.filter(id=entry_id,user=u)
                entry = etry[0]
                entry.entry_url = request.POST['entry_url']
                entry.entry_name = request.POST['entry_name']
                entry.text_content = request.POST['text_content']

                etags = Tag()
                existing_tags = etags.existing_tags(entry_id)
                for tag in existing_tags:
                    etags.remove_tag(tag[0])
                    
                taglist = manage_tags(request.POST['entry_tags'])
                add_tags(taglist,u,entry)

                entry.save()
                # update hyperestraier db
                try:
                    hyper_client = HyperClient(url=os.environ['RCACHE_HYPER_URL'])
                    hyper_client.doc_update(str(entry.id),entry)
                except Exception, e:
                    print unicode(e)
                
                url = "/detail/%s/" % entry.id
                return HttpResponseRedirect(url)
            else:
                #need to render_to_response the same as below with an error msg
                return HttpResponseRedirect("/edit/%s/"% entry_id)
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
                message = None
                return render_to_response('edit_entry.html',
                                          {'entry':e,
                                           'imgs':imgs,
                                           'links':links,
                                           'tags':tags_clean,
                                           'entry_tags':entry_tags,
                                           'user':u,
                                           'message':message})
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
            title = request.POST['title']
            tgs = request.POST['tags']
            etext = request.POST['entry_text']
            if request.FILES.has_key('the_file'):
                if request.FILES['the_file']:
                    #handle upload
                    file_data = request.FILES['the_file']['content']
                    file_name = request.FILES['the_file']['filename']

                    #if ttl == '':
                    title = _('%(ttl)s ** From file: %(file_name)s ** ') % \
                          {'ttl':title,'file_name':file_name} 

                    content_type = request.FILES['the_file']['content-type']
                    file_txt = _('***Error sccraping document: %(file_name)s ***') %\
                               {'file_name':file_name}

                    if content_type == 'application/msword':
                        file_txt = process_word(file_data,file_name)
                    elif content_type == 'application/pdf':
                        file_txt = process_pdf(file_data,file_name)
                    #elif content_type == 'text/plain':
                    #    file_txt = process_txt(file_data)
                    else:
                        pass
                etext = etext + _("\n------Scraped Text------\n") + file_txt
            if etext:    
                entry = Entry(entry_url=url,
                              entry_name=title,
                              text_content=etext,
                              user=u)
                entry.save()

                try:
                    hyper_client = HyperClient(url=os.environ['RCACHE_HYPER_URL'])
                    hyper_client.doc_add(entry)
                except Exception, e:
                    print unicode(e)
                
                #handle tags here!
                taglist = manage_tags(tgs)
                add_tags(taglist,u,entry)
                detail_url = "/detail/%s/" % entry.id
                return HttpResponseRedirect(detail_url)
            else:
                m=_("Please upload a file or enter some Entry Text.")
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
        
        if request.GET.has_key('search_str'):
            if request.GET['search_str']:
                params = request.GET['search_str']
                e = Entry()
                #entries = e.fulltxt(u,params)
                entries = e.hypersearch(params,u)
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

def search_xhr(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        
        if request.POST:
            if request.POST['search_str']:
                params = request.POST['search_str']
                e = Entry()
                entries = e.fulltxt(u,params)
                #fixme: entries need to be re-formatted for YUI
                data = {'result':'success','entries':entries}
                return HttpResponse(simplejson.dumps(data),
                        mimetype='application/javascript')
            else:
                data = {'result':'error','msg':_('Please Enter a Query')}
                return HttpResponse(simplejson.dumps(data),
                        mimetype='application/javascript')
        else:
            data = {'result':'error','msg':'POST Not GET!'}
            return HttpResponse(simplejson.dumps(data),
                                mimetype='application/javascript')
    else:
        data = {'result':'error','msg':_('ERROR: You are not logged in.')}
        return HttpResponse(simplejson.dumps(data),
                            mimetype='application/javascript')

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
            message = _('Success')
        else:
            message = _('Login Failed')
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
                                  {'server_url':SERVER_URL})

def login_err(request):
    error = _("Login Incorrect")
    if request.GET['err']:
        if request.GET['err'] == 'passwd':
            error = _("Login Failed: Please enter your password.")
        if request.GET['err'] == 'login':
            error = _("Login Failed: Please enter your login name.")
            
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

                    # add this entry to the hyper db
                    
                    try:
                        hyper_client = HyperClient(url=os.environ['RCACHE_HYPER_URL'])
                        hyper_client.doc_add(entry)
                        reactor.run()
                    except Exception, e:
                        print unicode(e)

                    return HttpResponse(simplejson.dumps('done'),
                                        mimetype='application/javascript')
                except Exception,e:
                    print e
                    json_dict=dict(status="error",entry_id=None,
                                   msg=_("Something Blew Up!: %(err)s")\
                                   % {'err':unicode(e)})
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
            err = _('Unknown Error')
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


def update_tags(new_tags,entry):
    """passed a list of tags, and an entry: find existing tags, compare to
    new_tags and remove the differnce or add new tags"""
    pass

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
            tag = tag.lower()
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

def process_word(data,filename):
    """pass word doc through antiword, save output text to entry, save original file in database"""
    tmp_name = antiword.save_tmp(data)
    try:
        the_text = antiword.extractText(tmp_name)
        return the_text
    except:
        return _("Error processing Word doc: %(filename)s") %\
               {'filename':filename}


def process_pdf(data,filename):
    """scrape text from PDF, store as an entry and Media record"""
    tmp_name = pdf.save_tmp(data)
    try:
        the_text = pdf.extractPDFText(tmp_name)
        return the_text
    except:
        return _("Error processing PDF file: %(filename)s") % {'filename':filename}
    

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


def tag_editor(request):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.POST:
            tags = []
            #lookup tags:
            tag_form = GetTagForm(dict(tag=request.POST['tag']))
            if tag_form.is_valid():
                tags = Tag.objects.filter(user=u,tag__icontains=request.POST['tag'])
                tag_form = None
            else:
                pass
        else:
            tags = None
            
            tag_form = GetTagForm()
            
        return render_to_response('tag_editor.html',
                                  {'user':u,
                                   'tag_form':tag_form,
                                   'tags':tags})
    else:
        return HttpResponseRedirect("/login_required/")

def tag_maint(request):
    """deal with empty tags - show empty tags here, also start tag editor UI"""
    if login_check(request):
        #get empty tags:
        u = User.objects.get(id=request.session['userid'])
        t = Tag()
        empty_tags = t.empty_tags(u)
        len_tgs = len(empty_tags)
        if len(empty_tags) > 0:
            tgs = True
        else:
            tgs = False
        return render_to_response('tag_maint.html',
                                  {'user':u,
                                   'empty_tags':empty_tags,
                                   'tgs':tgs,
                                   'len_tgs':len_tgs})
    else:
        return HttpResponseRedirect("/login_required/")

def tag_edit(request,tag_id):
    """Edit one tag"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.POST:
            try:
                
                form = TagForm(request.POST)
                if form.is_valid():
                    t = Tag.objects.filter(id=tag_id,user=u)
                    tag = t[0]
                    tag.tag = request.POST['tag']
                    tag.save()
                    msg = _("Success: Tag Updated")
                    return render_to_response('tag_edit.html',
                                              {'user':u,
                                               'tag':tag,
                                               'tag_id':tag_id,
                                               'form':form,
                                               'msg':msg})
                else:
                    raise Exception(_("ERROR: Something blew up."))
            except Exception, e:
                msg = _("Error: Could not update tag. Please contact the admin if this error repeats.")
                t = Tag.objects.filter(id=tag_id,user=u)
                tag = t[0]
                return render_to_response('tag_edit.html',
                                          {'user':u,
                                           'tag':tag.tag,
                                           'tag_id':tag.id,
                                           'msg':msg})
        else:
            
            t = Tag.objects.filter(id=tag_id,user=u)
            tag = t[0]
            form = TagForm(dict(tag=tag.tag))
            
            return render_to_response('tag_edit.html',
                                      {'user':u,
                                       'tag':tag,
                                       'tag_id':tag_id,
                                       'form':form})
    else:
        return HttpResponseRedirect("/login_required/")


def tag_remove(request,tag_id):
    """Edit one tag"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        try:
            t = Tag.objects.filter(id=tag_id,user=u)
            tag = t[0]
            tag.delete()
            msg = _("Success: Tag Removed")
            return render_to_response('tag_edit.html',
                                      {'user':u,
                                       'tag':tag,
                                       'msg':msg})
        except Exception, e:
            msg = _("Error: Could not remove tag. Please contact the admin if this error repeats.")
            t = Tag.objects.filter(id=tag_id,user=u)
            tag = t[0]
            return render_to_response('tag_edit.html',
                                      {'user':u,
                                       'tag':tag,
                                       'tag_id':tag_id,
                                       'msg':msg})
    else:
        return HttpResponseRedirect("/login_required/")

def remove_empty_tag(request,tag_id):
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        empty_tags = []
        try:
            t = Tag.objects.filter(user=u.id,id=tag_id)
            tag_name = t[0].tag
            t[0].delete()
            msg = _("Success: tag '%(tag_name)s' was removed") % {'tag_name':tag_name}
        except Exception, e:
            print str(e)
            msg = _("Error: Could not remove the Tag")
        t = Tag()
        empty_tags = t.empty_tags(u)
        len_tgs = len(empty_tags)
        if len(empty_tags) > 0:
            tgs = True
        else:
            tgs = False
        return render_to_response('tag_maint.html',
                                  {'user':u,
                                   'empty_tags':empty_tags,
                                   'msg':msg,
                                   'tgs':tgs,
                                   'len_tgs':len_tgs})
    else:
        return HttpResponseRedirect("/login_required/")
            
def remove_all_empty_tags(request):
    if login_check(request):
        try:
            u = User.objects.get(id=request.session['userid'])
            t = Tag()
            empty_tags = t.empty_tags(u)
            tlst = []
            for tag in empty_tags:
                tlst.append({'id':tag[1]})
            t.kill_tags(u,tlst)
            return HttpResponseRedirect("/filter/tags/maintenence/?all_tags_removed")
        except:
            return HttpResponseRedirect("/filter/tags/maintenence/?tag_removal_error")
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
                    try:
                        send_mail(_('rCache Account Application'),
                                  msg,
                                  'admin@rcache.com',
                                  [u.email,'admin@rcache.com',],
                                  fail_silently=False,auth_user=EMAIL_HOST_USER,
                                  auth_password=EMAIL_HOST_PASSWORD)
                    except Exception, e:
                        err = str(e)
                    return render_to_response('account_pending.html',{'message':m})
                else:
                    m = "Email address is not valid."
                return render_to_response('account.html',{'message':m})
                
            except Exception,e:
                m = _("An error occurred creating an account for %(email)s. Please send an email to admin at rcache dot com, please include this error message: %(err)s")\
                    % {'email':request.POST['email'],'err':err}
                return render_to_response('account.html',{'message':m})
        else:
            m = _("Please Enter your email address")
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
                  err.append(_("Password and Password Confirm do not match."))
                  render_to_response('myaccount.html',{'user':u,
                                                       'err':err})
          if request.POST['email']:
              try:
                  if isValidEmail(request.POST['email'],None):
                      u.email = request.POST['email']
              except:
                  err.append(_("Email Address is not valid."))
                  render_to_response('myaccount.html',{'user':u,
                                                         'err':err})
              u.blogurl = request.POST['blogurl']
              u.website = request.POST['website']
              u.first_name = request.POST['first_name']
              u.last_name = request.POST['last_name']
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

    
def feed(request, url, feed_dict=None):
    if login_check(request):
        if not feed_dict:
            raise Http404, _("No feeds are registered.")

        try:
            slug, param = url.split('/', 1)
        except ValueError:
            slug, param = url, ''

        try:
            f = feed_dict[slug]
        except KeyError:
            raise Http404, _("Slug %(slug)r isn't registered.") % {'slug':slug}

        try:
            feedgen = f(slug, request).get_feed(param)
        except feeds.FeedDoesNotExist:
            raise Http404, _("Invalid feed parameters. Slug %(slug)r is valid, but other parameters, or lack thereof, are not.") % {'slug':slug}

        response = HttpResponse(mimetype=feedgen.mime_type)
        feedgen.write(response, 'utf-8')
        return response
    else:
        #fixme: make this a feed with a url to login
        return HttpResponseRedirect("/login_required/")

def server(request):
    return render_to_response('server.html',dict())

def commentary(request,entry_id):
    """Lookup any existing commentary for this entry,
    or show form to create new commentary"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.POST:
            #create commentary object
            posted_data = copy.deepcopy(request.POST)
            CommForm = forms.models.form_for_model(Commentary)
            cform = CommForm(posted_data)
            if cform.is_valid():
                commentary = cform.save()
                #redirect to make snippits
                return HttpResponseRedirect("/commentary/makesnippets/%s" \
                                            % commentary.id)
            else:
                #form not valid??
                cform.fields['user'].widget = forms.widgets.HiddenInput(attrs={'class':'hidden_input'})
                cform.fields['entry'].widget = forms.widgets.HiddenInput(attrs={'class':'hidden_input'})
                cform.fields['title'].widget = forms.widgets.Textarea(attrs={'cols':'60','rows':'2'})
                cform.fields['summary'].widget = forms.widgets.Textarea(attrs={'cols':'60','rows':'4'})
                e = Entry.objects.filter(user=u,id=request.POST['entry'])
                tags_clean= tags_cleaned(e[0])
                etc = escape(e[0].text_content)
                return render_to_response('new_commentary.html',
                                          {'user':u,
                                           'entry':e,
                                           'escaped_text_content':etc,
                                           'tags':tags_clean,
                                           'cform':cform})
                
        else:
            try:
                e = Entry.objects.filter(user=u,id=entry_id)
                tags_clean= tags_cleaned(e[0])
                etc = escape(e[0].text_content)
                #lookup commentary
                c = Commentary.objects.filter(user=u,entry=e[0])
                if len(c) > 0:
                    #display existing commentary
                    return render_to_response('commentary.html',
                                              {'user':u,
                                               'commentary':c,
                                               'entry':e,
                                               'escaped_text_content':etc,})
                else:
                    #display form to create new commentary
                    raise Exception(_("No existing commentaries"))
            except Exception,err:
                print err
                title = _("Commentary on '%(entry_name)s'") \
                        % {'entry_name':e[0].entry_name}
                initial_data = {'user':u.id,
                                'entry':entry_id,
                                'title':title,
                                'summary':None}
                cform = CommentaryForm(initial_data)
                cform.fields['user'].widget = forms.widgets.HiddenInput(attrs={'class':'hidden_input'})
                cform.fields['entry'].widget = forms.widgets.HiddenInput(attrs={'class':'hidden_input'})
                cform.fields['title'].widget = forms.widgets.Textarea(attrs={'cols':'60','rows':'2'})
                cform.fields['summary'].widget = forms.widgets.Textarea(attrs={'cols':'60','rows':'4'})
                return render_to_response('new_commentary.html',
                                          {'user':u,
                                           'entry':e,
                                           'escaped_text_content':etc,
                                           'tags':tags_clean,
                                           'cform':cform}) 
    else:
        return HttpResponseRedirect("/login_required/")

def commentary_make_snippets(request,commentary_id):
    """after initial commentary object is created - redirect here to make snippits automatically."""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        #generate snippets here
        #get entry from commentary ID
        comm = Commentary.objects.filter(user=u,id=commentary_id)
        #try:
        #split entry.text_content on '\n'
        raw_snips = comm[0].entry.text_content.split("\n")
        #for each non empty list item make a snippet
        for snip in raw_snips:
            snip.strip()
            sortordr = 0
            if snip:
                sortordr += 1000
                s = Snippet(user=u,
                            entry=comm[0].entry,
                            snippet=snip,
                            sortorder=sortordr,
                            commentary=comm[0])
                s.save()
        #display commentary detail page
        return HttpResponseRedirect("/commentary/detail/%s/"\
                                    % commentary_id)
        
        #except Exception, e:
            #cannot get entry or snippets... fail to ???
            #print e
            #pass
        
    
    else:
        return HttpResponseRedirect("/login_required/")

def collector(request):
    """
    info page about the collector
    """
    return render_to_response('collector.html',{})

    
def commentary_detail(request,commentary_id):
    """Display the commentary detail, all snippets and all of the comments per snippets"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        #lookup commentary
        comm = Commentary.objects.filter(user=u,id=commentary_id)
        #lookup snippets
        snips = Snippet.objects.filter(commentary=comm[0]).order_by('id')
        #lookup original article
        entry = comm[0].entry
        etc = escape(entry.text_content)
        tags_clean = tags_cleaned(entry)
        #display commentary header/title/summary, list snippets in divs,
        #add a control div between each div to provide delete,
        #add comment controls
        return render_to_response('commentary_detail.html',
                                  {'user':u,
                                   'entry':entry,
                                   'escaped_text_content':etc,
                                   'tags':tags_clean,
                                   'commentary':comm,
                                   'snippets':snips})
    else:
        return HttpResponseRedirect("/login_required/")

def tags_cleaned(entry):
    tags = Tag.objects.filter(entry__exact=entry)
    tags_clean = []
    for t in tags:
        tags_clean.append(t.tag)
    tags_clean = dict.fromkeys(tags_clean).keys()
    return tags_clean

def snippet_xhr(request,snippet_id):
    """return JSON obj: snippet and related comments"""
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        snip = Snippet.objects.filter(id=snippet_id,user=u)
        thesnippet = snip[0]
        thesnippet.active = 1
        thesnippet.save()
        comments = Comment.objects.filter(snippet=thesnippet).order_by('id')
        c = []
        for comm in comments:
            c.append({'id':comm.id,
                      'parent':comm.parent.id,
                      'comment':comm.comment,
                      'user':comm.user.login
                      })
        
        json_dict = dict(snippet={'snippet':thesnippet.snippet,
                                  'id':thesnippet.id,
                                  'active':thesnippet.active,
                                  },
                         comments=c)
        
        return HttpResponse(simplejson.dumps(json_dict),
                            mimetype='application/javascript')
        
    else:
        return HttpResponseRedirect("/login_required/")

def snippet_hide_xhr(request,snippet_id):
    """return JSON obj: snippet and related comments"""
    if login_check(request):
        
        u = User.objects.get(id=request.session['userid'])
        snip = Snippet.objects.filter(id=snippet_id,user=u)
        thesnippet = snip[0]
        thesnippet.active = 0
        thesnippet.save()
        print "Active = %s" % thesnippet.active
        return HttpResponse(simplejson.dumps({'result':True}),
                            mimetype='application/javascript')
    else:
        return HttpResponseRedirect("/login_required/")

def comment_new_xhr(request):
    """Post - only interface to add a new comment"""
    if login_check(request):
        if request.POST:
            #try:
            u = User.objects.get(id=request.session['userid'])
            snip = Snippet.objects.filter(id=request.POST['snippet'])
            s = snip[0]
            try:
                parent = Comment.objects.filter(user=u,id=request.POST.parent)
                p = parent[0].id
                sortorder = p.sortorder + 1000
            except:
                p = None
                sortorder = 0

            comment = Comment(user=u,
                              parent=p,
                              snippet=s,
                              comment=request.POST['comment'],
                              sortorder=sortorder)
            comment.save()
            return HttpResponse(
                simplejson.dumps({'result':'Success',
                                  'message':'Comment entered',
                                  'comment':comment.comment,
                                  'comment_id':comment.id,
                                  'comment_user':comment.user.login,
                                  'snippet_id':comment.snippet.id}),
                mimetype='application/javascript')
                
            #except:
            #    return HttpResponse(simplejson.dumps({'result':'Error',
            #                                          'message':'Coould not create comment.'}),
            #                        mimetype='application/javascript')
        else:
            return HttpResponse(
                simplejson.dumps({'result':'Failure',
                                  'message':'Comment NOT entered - Use POST not GET',}),
                mimetype='application/javascript')
    else:
        return HttpResponseRedirect("/login_required/")

def smtp_google():
    
    #from django.core.mail import send_mail
    subject = "Testing Google SMTP"
    message = "Test message"
    from_email = 'admin@rcache.com'
    recipient_list = ['david@ddahl.com',]
    send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=EMAIL_HOST_USER,
              auth_password=EMAIL_HOST_PASSWORD)

def save_link(request):
    """
    accept incoming link from users via bookmarklet
    """
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        if request.GET['url']:
            # ok we have the minimum amount of data to store
            url = request.GET['url']
            try:
                title = request.GET['title']
            except:
                title = ''
            try:
                comment = request.GET['comment']
            except:
                comment = ''
            try:
                keywords = request.GET['keywords']
            except:
                keywords = ''
            try:
                description = request.GET['description']
            except:
                description = ''
            try:
                lnk = SavedLink.objects.create(user=u,
                                               url=url,
                                               title=title,
                                               comment=comment,
                                               keywords=keywords,
                                               description=description)
                print "Link Saved: %s %s" %(lnk.id,url,)
                return HttpResponseRedirect(url) 
            except Exception,e:
                print e
                return HttpResponse(str(e))
    else:
        return HttpResponseRedirect("/login_required/") 
