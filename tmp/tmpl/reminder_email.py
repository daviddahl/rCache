from django.core.mail import send_mail

from rcache.models import *

def user_data():
    user_lst = [] 
    emails = []
    users = User.objects.filter(password__exact='no passwd yet',date_created__lt='2007-03-23')
    for user in users:
        evt = UserEvent.objects.filter(event_type__exact='Accept Account',
                                       user=user)
        for e in evt:
            if e.event_type == 'Accept Account':
                user_lst.append({'user':user,'evt':evt[0]})
    
    return user_lst

def send(user,evt):
    msg = mk_tmpl(user.login,evt.event_date,evt.hash_key)
    print "Sending..."
    send_mail('re: rCache Account Activation (re-sent)',
             msg,
             'admin@rcache.com',
             [user.login,'admin@rcache.com',],
             fail_silently=True)
    print msg
    print "Done...\n\n"

def mk_tmpl(login,date_time,hash_key):
    link = 'https://collect.rcache.com/accounts/activate/?hk=%s' % hash_key

    tmpl = """Dear %s,\n\nAccording to our records, on %s, you applied for an rCache Account at http://www.rcache.com. In order to activate your free rCache research account, you must click on this link:\n\n %s\n\nIf you would not like to activate your account please reply to this email with *Cancel my account* in the subject line.\n\nBest Regards,\n\nDavid Dahl\n\nDeveloper, rCache.com\n\nrCache.com, Your personal research repository""" % (login, str(date_time), link, )
    return tmpl

def send_all(user_lst):
    for dct in user_lst:
        send(dct['user'],dct['evt'])


user_list = user_data()
send_all(user_list)
