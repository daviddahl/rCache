"""fixme: need to add cron job that closes all UserEvents 48 hours after being opened."""

import os
import sys
import re
import md5
import sha
import time
from django.contrib.auth import authenticate, login
from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.utils import simplejson
from django.core.validators import email_re
from django.core.mail import send_mail

from rcache.models import *


def login_required(request):
    return render_to_response('account_login_required.html',{})

def admin_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect("/accounts/dashboard/")
            else:
                # Return a 'disabled account' error message
                return HttpResponseRedirect("/accounts/admin_disabled/")
        else:
            # Return an 'invalid login' error message.
            return HttpResponseRedirect("/accounts/login_required/")
    else:
        return render_to_response('admin_login.html',{})
    

def admin_acct_disabled(request):
    pass

def admin_login_req(request):
    pass

def dashboard(request):
    """Display grid of inactive applied for users and a grid of currently active users. Sort by number of entries. allow admin to select an inactive user and activate them. an email is sent out with a link. once clicked user is brought back to rcache to enter and confirm his or her password."""
    if request.user.is_authenticated():
        # Do something for authenticated users.
        new_users = User.objects.filter(password__exact='')
        users = User.objects.filter(active__exact=1)
        return render_to_response('dashboard.html',
                                  {'users':users,
                                   'new_users':new_users})
    else:
        # Do something for anonymous users.
        return HttpResponseRedirect("/accounts/login_required/")


def new_account(request):
    """send an email to user to accept account and create password
    create UserEvent and send email for new user"""
    pass

def approve_password(password):
    """check password with regex or whatever"""
    pass

def activation(request,user_id):
    if request.POST:
        pass
    else:
        user = User.objects.get(id=user_id)
        return render_to_response('activation.html',
                                  {'user':user})
    
def activation_yes(request,user_id):
    if request.user.is_authenticated():
        try:
            user = User.objects.get(id=user_id)
            hk = hash_key(user)

            evt = UserEvent(user=user,
                            hash_key=hk,
                            event_type='Accept Account')
            evt.save()
            #send_email
            msg = """Dear %s,\n\nThank you for applying for an rCache account. It is ready to use. Please click on this link to activate:\n\nhttps://collect.rcache.com/accounts/activate/?hk=%s\n\nBest Regards,\n\nrCache Activation Bot\n\n\nrCache.com: your personal search repository""" \
                  % (user.login,hk,)

            send_mail('rCache Account Activation',
                      msg,
                      'donotreply@rcache.com',
                      [user.email,'admin@rcache.com',],
                      fail_silently=False)
            message ="Activation Successful."
            return render_to_response('activation_yes.html',
                                      {'user':user})
        except Exception,e:
            #remove UserEvent
            try:
                event = UserEvent.objects.get(id=evt.id)
                event.delete()
            except:
                pass
                
            return render_to_response('activation.html',
                                      {'user':user,
                                       'message':e})
    else:
        return HttpResponseRedirect("/accounts/login_required/")


def hash_key(user):
    #take datetime and userid to generate a SHA hash
    id = str(user.id)
    the_time = str(time.time())
    str_to_hash = """%s%s%s""" % (id,user.login,the_time,)
    mysha = sha.new(unicode(str_to_hash))
    user_sha_hash = mysha.hexdigest()
    return user_sha_hash
     
def activate(request):
    """lookup UserEvent if found and open and type is 'accept account'
    display form for user to set password"""
    if request.POST:
        #lookup user:
        evt = UserEvent.objects.filter(hash_key__exact=request.POST['hk'])
        if evt[0].open:
            pass
        else:
            return HttpResponseRedirect("/accounts/err/?e=EVENT_CLOSED")
        if request.POST['password'] and request.POST['password_conf']:
            if request.POST['password'] == request.POST['password_conf']:
                if len(request.POST['password']) >5:
                    pass
                else:
                    return HttpResponseRedirect("/accounts/err/?e=PASSWD_ERR")
                try:
                    user = evt[0].user
                    pw_sha = sha.new(unicode(request.POST['password']))
                    password_enc = pw_sha.hexdigest()
                    user.password = password_enc
                    user.active = 1
                    user.save()
                    evt[0].open = False
                    evt[0].save()
                    #fixme: send email again!
                    return render_to_response('account_ready.html',
                                              {'hk':request.POST['hk'],
                                               'user':evt[0].user})
                except:
                    return HttpResponseRedirect("/accounts/err/?e=GET_USER_ERR")
            else:
                m = "Your Password and Confirm Password do not match."
                return render_to_response('finalize.html',
                                          {'hk':request.POST['hk'],
                                           'user':evt[0].user,
                                           'message':m})
        else:
            m = "Please enter a Password and Confirm the Password."
            return render_to_response('finalize.html',
                                      {'hk':request.POST['hk'],
                                       'user':evt[0].user,
                                       'message':m})
    else:
        if request.GET.has_key('hk'):
            #lookup event
            event = UserEvent.objects.filter(hash_key__exact=request.GET['hk'])
            if len(event) == 1:
                if event[0].open:
                    pass
                else:
                    return HttpResponseRedirect("/accounts/err/?e=EVENT_CLOSED")
                return render_to_response('finalize.html',
                                          {'hk':request.GET['hk'],
                                           'user':event[0].user})
            else:
                return HttpResponseRedirect("/accounts/err/?e=HK_DOES_NOT_EXIST")
        else:
            return HttpResponseRedirect("/accounts/err/?e=HK_DOES_NOT_EXIST")
            
def detail(request,user_id):
    if request.user.is_authenticated():
        try:
            user = User.objects.get(id=user_id)
            events = UserEvent.objects.get(id=user_id)
            return render_to_response('user_detail.html',
                                      {'user':user,
                                       'events':events})
        except Exception, e:
            return render_to_response('user_detail.html',
                                      {'message':e})
    else:
        return HttpResponseRedirect("/accounts/login_required/")
        

def error_txt(e):
    errs = {'HK_DOES_NOT_EXIST':"Your account activation key was not found in the database. Please contact us about this error code.",
            'GET_USER_ERR':"Your user account application coild not be found. Please contact us about this error.",
            'EVENT_CLOSED':"Your account is already activated.",
            'PASSWD_ERR':"Your password is not formatted correctly. It must be at least 6 characters ion length.",
            'HKPASSWD_DOES_NOT_EXIST':"Your password change key was not found in the database. Please contact us about this error code.",}
    try:
        return errs[e]
    except:
        return "An unknown erorr occurred while attempting to activate your account. Please contact us about this error."

def acct_err(request):
    if request.GET.has_key('e'):
        err = error_txt(request.GET['e'])
    else:
        err = "An unknown erorr occurred while attempting to activate your account. Please contact us about this error."
        
    return render_to_response('acct_err.html',
                              {'message':err})

def password(request):
    if request.POST:
        if request.POST['login']:
            #lookup user
            user = User.objects.filter(login__exact=request.POST['login'])
            if len(user) == 1:
                if user[0].login == request.POST['login']:
                    #create userevent
                    hk = hash_key(user[0])
                    evt = UserEvent(user=user[0],
                                    hash_key=hk,
                                    event_type='Password Change Request')
                    evt.save()
                    #send_email
                    msg = """Dear %s,\n\nOur records indicate that you have requested a password change for rCache. Please click on this link to make the requested change:\n\nhttps://collect.rcache.com/accounts/password/change/?hk=%s\n\nBest Regards,\n\nrCache System Bot\n\n\nrCache.com: your personal search repository""" \
                          % (user[0].login,hk,)

                    send_mail('rCache Password Change',
                              msg,
                              'donotreply@rcache.com',
                              [user[0].email,'admin@rcache.com',],
                              fail_silently=False)
                    message ="An Email has been sent to you with directions to change your password"
                    return render_to_response('password_reset.html',
                                              {'message':message,
                                               'email_sent':True})
                    #send email with link
                else:
                    #something is wrong!
                    #fixme: send email to admin about this
                    #or create a userevent called "anomoly"
                    m="Please make sure you entered your Login correctly"
                    return render_to_response('password_reset.html',{'message':m})
            else:
                #wrong count for users
                m="Please make sure you entered your Login correctly"
                return render_to_response('password_reset.html',{'message':m})
        else:
            m="Please enter your rCache Login (Your Login is the email address you signed up with.)"
            return render_to_response('password_reset.html',{'message':m})
    else:
        return render_to_response('password_reset.html',{})

def password_change(request):
    """Lookup user via hashkey (request.GET['hk']) in UserEvent. If user is in good standing (active is True) present form to change the user's password"""
    if request.POST:
        #lookup UserEvent
        evt = UserEvent.objects.filter(hash_key__exact=request.POST['hk'])
        if evt is not None:
            if len(evt) == 1:
                if evt[0].open:
                    pass
                else:
                    return HttpResponseRedirect("/accounts/err/?e=EVENT_CLOSED")
            else:
                return HttpResponseRedirect("/accounts/err/?e=GET_USER_ERR")
        else:
            return HttpResponseRedirect("/accounts/err/?e=GET_USER_ERR")
        if request.POST['password'] and request.POST['password_conf']:
            if request.POST['password'] == request.POST['password_conf']:
                if len(request.POST['password']) >5:
                    pass
                else:
                    return HttpResponseRedirect("/accounts/err/?e=PASSWD_ERR")
                try:
                    user = evt[0].user
                    pw_sha = sha.new(unicode(request.POST['password']))
                    password_enc = pw_sha.hexdigest()
                    user.password = password_enc
                    user.active = 1
                    user.save()
                    evt[0].open = False
                    evt[0].save()
                    #fixme: send email again!
                    return render_to_response('password_changed.html',
                                              {'hk':request.POST['hk'],
                                               'user':evt[0].user})
                except:
                    return HttpResponseRedirect("/accounts/err/?e=GET_USER_ERR")
            else:
                m = "Your Password and Confirm Password do not match."
                return render_to_response('password_update.html',
                                          {'hk':request.POST['hk'],
                                           'user':evt[0].user,
                                           'message':m})
        else:
            m = "Please enter a Password and Confirm the Password."
            return render_to_response('password_update.html',
                                      {'hk':request.POST['hk'],
                                       'user':evt[0].user,
                                       'message':m})
    
    else:
        if request.GET.has_key('hk'):
            event = UserEvent.objects.filter(hash_key__exact=request.GET['hk'])
            if len(event) == 1:
                if event[0].open:
                    pass
                else:
                    return HttpResponseRedirect("/accounts/err/?e=EVENT_CLOSED")
                return render_to_response('password_update.html',
                                          {'hk':request.GET['hk']})
            else:
                return HttpResponseRedirect("/accounts/err/?e=HKPASSWD_DOES_NOT_EXIST")
        else:
            return HttpResponseRedirect("/accounts/err/?e=HKPASSWD_DOES_NOT_EXIST")
