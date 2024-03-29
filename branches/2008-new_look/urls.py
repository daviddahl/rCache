import os
from django.conf.urls.defaults import *
from rcache.rss import LatestEntries, LatestEntriesByTag

feeds = {
    'recent': LatestEntries,
    'tag': LatestEntriesByTag,
}

js_info_dict = {
    'packages': ('rcache',),
}

urlpatterns = patterns('',
                       (r'^jsi18n/(?P<packages>\S+?)/$',
                        'django.views.i18n.javascript_catalog'),
                       )

urlpatterns += patterns('rcache.views',
                        (r'^admin/', include('django.contrib.admin.urls')),
                        (r'^$', 'index'),
                        (r'^cache/$', 'cache'),
                        (r'^server/$', 'server'),
                        (r'^contact/$', 'contact'),
                        (r'^agreement/$', 'agreement'),
                        (r'^privacy/$', 'privacy'),
                        (r'^new/$', 'new_entry'),
                        (r'^edit/(?P<entry_id>\d+)/$', 'edit_entry'),
                        (r'^commentary/(?P<entry_id>\d+)/$', 'commentary'),
                        (r'^commentary/makesnippets/(?P<commentary_id>\d+)/$',
                         'commentary_make_snippets'),
                        (r'^commentary/detail/(?P<commentary_id>\d+)/$',
                         'commentary_detail'),
                        (r'^commentary/snippet_xhr/(?P<snippet_id>\d+)/$',
                         'snippet_xhr'),
                        (r'^commentary/snippet_hide_xhr/(?P<snippet_id>\d+)/$',
                         'snippet_hide_xhr'),
                        (r'^commentary/comment_new_xhr/$','comment_new_xhr'),
                        (r'^404/$', 'not_found'),
                        (r'^error/$', 'err_unknown'),
                        (r'^search/$', 'search'),
                        (r'^postcache/$', 'postcache'),
                        (r'^bookmarklet/$', 'bookmarklet'),
                        (r'^spider/$', 'spider'),
                        (r'^recent/$','recent'),
                        (r'^rss/(?P<url>.*)/$', 'feed', {'feed_dict': feeds}),
                        (r'^colleagues/$','colleagues'),
                        (r'^colleague/new/$','new_colleague'),
                        (r'^colleague/(?P<coll_id>\d+)/research/$', 'colleague_research'),
                        (r'^colleague/(?P<coll_id>\d+)/research/tag/$', 'colleague_research_tag'),
                        (r'^colleague/(?P<coll_id>\d+)/research/search/$', 'colleague_research_keywords'),
                        (r'^colleague/(?P<coll_id>\d+)/detail/(?P<entry_id>\d+)/$', 'colleague_research_detail'),
                        (r'^colleague/(?P<coll_id>\d+)/$', 'colleague_detail'),
                        #(r'^colleague/(?P<coll_id>\d+)/update/$', 'colleague_detail'),
                        (r'^update_colleague/$', 'colleague_detail'),
                        (r'^recent_xhr/$','recent_xhr'),
                        (r'^recent_original/$','recent_original'),
                        (r'^login/$','login'),
                        (r'^loginxul/$','loginxul'),
                        (r'^logout/$','logout'),
                        (r'^login_check/$','login_check_svc'),
                        (r'^login_err/$','login_err'),
                        (r'^login_required/$','login_required'),
                        (r'^detail/(?P<entry_id>\d+)/$','detail'),
                        (r'^remove/(?P<entry_id>\d+)/$','remove_entry'),
                        (r'^removeit/(?P<entry_id>\d+)/$','removeit'),
                        (r'^save/link/$','save_link'),
                        (r'^removed/$','remove_entry'),
                        (r'^tag/$','tag'),
                        (r'^taglist/$','tag_list'),
                        (r'^filter/$','tag_list'),
                        (r'^filter/tags/$','tag_list'),
                        (r'^filter/tags/editor/$','tag_editor'),
                        (r'^filter/tags/edit/(?P<tag_id>\d+)/$','tag_edit'),
                        (r'^filter/tags/remove/(?P<tag_id>\d+)/$','tag_remove'),
                        (r'^filter/tags/maintenence/$','tag_maint'),
                        (r'^filter/tags/maintenence/remove_empty_tag/(?P<tag_id>\d+)/$','remove_empty_tag'),
                        (r'^filter/tags/maintenence/remove_all_empty_tags/$','remove_all_empty_tags'),
                        (r'^filter/domains/$','domain_list'),
                        (r'^filter/domain_results/$','domain_filter'),
                        (r'^saved/links/$','saved_links'),
                        (r'^firefox/$','firefox'),
                        (r'^about/$','about'),
                        (r'^instructions/$','instructions'),
                        (r'^account/$','account_new'),
                        (r'^myaccount/$','myaccount'),
                        (r'^password/$','lost_password'),
                        (r'^collector/$','collector'),
                        )

urlpatterns += patterns('',
                        (r'^media/(.*)$',
                         'django.views.static.serve',
                         {'document_root': os.environ['RCACHE_DJANGO_MEDIA_ROOT'], 'show_indexes': False}),
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

urlpatterns += patterns('rcache.hyper.views',
                        (r'^hyper/search/$', 'search'),
                       )

urlpatterns += patterns('rcache.xhr.views',
                        (r'^xhr/search/$', 'hypersearch'),
                        (r'^xhr/entries/with/link/(?P<link_id>\d+)/$', 'entries_with_link'),

                        (r'^recentgrid/', 'recentgrid'),
                        )

urlpatterns += patterns('rcache.viz.views',
                        (r'^viz/$', 'index'),
                        (r'^viz/xhr/recent/tagged/with/(?P<tag_id>\d+)/$', 'recent_tagged_with'),
                        )

