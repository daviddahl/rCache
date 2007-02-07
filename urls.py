import os
from django.conf.urls.defaults import *

urlpatterns = patterns('rcache.views',
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'^$', 'index'),
                       (r'^cache/$', 'cache'),
                       (r'^contact/$', 'contact'),
                       (r'^agreement/$', 'agreement'),
                       (r'^privacy/$', 'privacy'),
                       (r'^new/$', 'new_entry'),
                       (r'^edit/(?P<entry_id>\d+)/$', 'edit_entry'),
                       (r'^404/$', 'not_found'),
                       (r'^error/$', 'err_unknown'),
                       (r'^search/$', 'search'),
                       (r'^postcache/$', 'postcache'),
                       (r'^bookmarklet/$', 'bookmarklet'),
                       (r'^spider/$', 'spider'),
                       (r'^recent/$','recent'),
                       (r'^recent_xhr/$','recent_xhr'),
                       (r'^login/$','login'),
                       (r'^loginxul/$','loginxul'),
                       (r'^logout/$','logout'),
                       (r'^login_check/$','login_check_svc'),
                       (r'^login_err/$','login_err'),
                       (r'^login_required/$','login_required'),
                       (r'^detail/(?P<entry_id>\d+)/$','detail'),
                       (r'^remove/(?P<entry_id>\d+)/$','remove_entry'),
                       (r'^removeit/(?P<entry_id>\d+)/$','removeit'),

                       (r'^removed/$','remove_entry'),
                       (r'^tag/$','tag'),
                       (r'^taglist/$','tag_list'),
                       (r'^filter/$','tag_list'),
                       (r'^filter/tags/$','tag_list'),
                       (r'^filter/domains/$','domain_list'),
                       (r'^filter/domain_results/$','domain_filter'),
                       (r'^firefox/$','firefox'),
                       (r'^about/$','about'),
                       (r'^instructions/$','instructions'),
                       (r'^account/$','account_new'),
                       (r'^myaccount/$','myaccount'),
                       (r'^password/$','lost_password'),
                       )
urlpatterns += patterns('',
                        (r'^media/(.*)$',
                        'django.views.static.serve',
                        {'document_root': os.environ['RCACHE_DJANGO_MEDIA_ROOT'], 'show_indexes': True}),
                        )
urlpatterns += patterns('rcache.account.views',
                        (r'^accounts/dashboard/$', 'dashboard'),
                        (r'^accounts/$', 'admin_login'),
                        (r'^accounts/login_required/$', 'login_required'),
                        (r'^accounts/activation/(?P<user_id>\d+)/$','activation'),
                        (r'^accounts/activation/(?P<user_id>\d+)/yes/$','activation_yes'),
                        (r'^accounts/activate/$','activate'),
                        (r'^accounts/err/$','acct_err'),
                        (r'^accounts/password/$','password'),
                        (r'^accounts/password/change/$','password_change'),
                        (r'^accounts/detail/(?P<user_id>\d+)/$','detail'),
                       )
