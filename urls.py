import os
from django.conf.urls.defaults import *

urlpatterns = patterns('rcache.views',
                       (r'^admin/', include('django.contrib.admin.urls')),
                       (r'^$', 'index'),
                       (r'^cache/$', 'cache'),
                       (r'^postcache/$', 'postcache'),
                       (r'^bookmarklet/$', 'bookmarklet'),
                       (r'^spider/$', 'spider'),
                       (r'^recent/$','recent'),
                       (r'^detail/(?P<entry_id>\d+)/$','detail'),
                       )
urlpatterns += patterns('',
                        (r'^media/(.*)$',
                        'django.views.static.serve',
                        {'document_root': os.environ['RCACHE_DJANGO_MEDIA_ROOT'], 'show_indexes': True}),
                        )
