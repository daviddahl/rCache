import re

from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django import forms
from django.utils import simplejson
from django.core.validators import email_re
from django.core.mail import send_mail
from django.contrib.syndication import feeds
from django import newforms as forms

from rcache.models import *
from rcache.views import login_check
from rcache.forms import *
from rcache.settings import *
from rcache.hyper.client import HyperClient
from rcache.xhr.jsonresponse import JsonResponse

def hypersearch(request):
    """
    do a hyper estraier search - return a list of dicts
    """
    if login_check(request):
        u = User.objects.get(id=request.session['userid'])
        
        try:
            params = request.POST['search_str']
            # remove ' AND ' from the end of the query
            params = re.sub(' AND $','',params)
            #print params
            e = Entry()
            entries = e.hypersearch(params,u)
            
            #print "entries: %s" % entries
            results = []
            search_count = len(entries)
            for entry in entries:
                results.append({'title':entry.entry_name,
                                'date_created':entry.date_created,
                                'attrs':entry.hyper_attrs,
                                'id':entry.id})
                
            res = render_to_string('related_docs.html',
                                   {'results':results,
                                    'length':len(results),
                                    'keywords':params,
                                    'search_count':search_count})
            #print "res: ", res
            return JsonResponse({'status':'success',
                                 'msg':res})
        except Exception, e:
            return JsonResponse({'status':'failure',
                                 'msg':str(e)})
    else:
        return JsonResponse({'status':'failure',
                             'msg':"Not Logged In, good try."})

def entries_with_link(request,link_id):
    """
    return rendered html snippet with all entries that also contain x link
    """
    try:
        u = User.objects.get(id=request.session['userid'])
        link = EntryUrl.objects.filter(user=u,id=link_id)[0]
        print link
        entries = EntryUrl.objects.filter(user=u,url=link.url)

        entry_list = render_to_string("entries_with_link.html",
                                      {'entry_list':entries})
        print entry_list
        if len(entry_list) == 0:
            return JsonResponse({'status':'failure','entries':entry_list})
        return JsonResponse({'status':'success','entries':entry_list,
                             'link_id':link.id})

    except Exception,e:
        print str(e)
        return JsonResponse({'status':'failure','msg':'No entries found'})

def recentgrid(request):
    """
    return html table for ingrid to parse for recent entries
    """
    try:
        u = User.objects.get(id=request.session['userid'])
        entries = Entry.objects.filter(user=u).order_by('-id')[:20]
        entry_list = render_to_string("recentgrid.html",
                                      {'entries':entries})
        return HttpResponse(entry_list)
    except Exception, e:
        print e
        return JsonResponse('Error: %s' % str(e))
