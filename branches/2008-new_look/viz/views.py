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
from codecs import encode, decode

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
from django.template.loader import render_to_string

from rcache.xhr.jsonresponse import JsonResponse
from rcache.models import *
from rcache.hyper.client import HyperClient, SearchError


def index(request):
    """
    start viz module as an experiment
    """
    #tags = Tag.objects.all().order_by('-tag_count')[:20]
    t = Tag()
    tags = t.tag_popularity(request.session['userid'])
    # returns: (tag_id,tag,count)
    return render_to_response("viz/index.html",{'tags':tags})


def recent_tagged_with(request,tag_id):
    """
    get 10 latest articles tagged with tag
    """
    try:
        u = User.objects.get(pk=request.session['userid'])
        t = Tag.objects.get(pk=tag_id)
        e = Entry.objects.filter(user=u,tag=t).order_by('-id')[:10]
        html = render_to_string("viz/recent_tagged_with.html",{'entries':e})
        return JsonResponse({'status':'success','msg':html})
    except Exception,e:
        return JsonResponse({'status':'failure','msg':str(e)})
