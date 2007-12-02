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
            print params
            e = Entry()
            entries = e.hypersearch(params,u)
            print "entries: %s" % entries
            results = []
            for entry in entries:
                results.append({'title':entry.entry_name,
                                'date_created':entry.date_created,
                                'attrs':entry.hyper_attrs,
                                'id':entry.id})
            res = render_to_string('related_docs.html',
                                   {'results':results})
            print "res: ", res
            return JsonResponse({'status':'success',
                                 'msg':res})
        except Exception, e:
            return JsonResponse({'status':'failure',
                                 'msg':str(e)})
    else:
        return JsonResponse({'status':'failure',
                             'msg':"Not Logged In, good try."})
