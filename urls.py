import os
from django.conf.urls.defaults import *

urlpatterns = patterns('rcache.views',
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'^$', 'index'),
                       (r'^cache/$', 'cache'),
                       (r'^new/$', 'new_entry'),
                       (r'^postcache/$', 'postcache'),
                       (r'^bookmarklet/$', 'bookmarklet'),
                       (r'^spider/$', 'spider'),
                       (r'^recent/$','recent'),
                       (r'^recent_xhr/$','recent_xhr'),
                       (r'^login/$','login'),
                       (r'^logout/$','logout'),
                       (r'^login_check/$','login_check_svc'),
                       (r'^login_err/$','login_err'),
                       (r'^login_required/$','login_required'),
                       (r'^detail/(?P<entry_id>\d+)/$','detail'),
                       )
urlpatterns += patterns('',
                        (r'^media/(.*)$',
                        'django.views.static.serve',
                        {'document_root': os.environ['RCACHE_DJANGO_MEDIA_ROOT'], 'show_indexes': True}),
                        )
