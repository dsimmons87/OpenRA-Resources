"""openra URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

from openra import views, api, ajax


urlpatterns = [
    # path(r'^admin/', admin.site.urls),

    path('', views.index, name='index'),

    path('maps/', views.maps, name='maps'),
    path('maps/<int:map_id>/', views.displayMap, name='displayMap'),
    path('maps/<int:map_id>/minimap/', views.serveMinimap, name='serveMinimap'),
    path('maps/<int:map_id>/oramap/', views.serveOramap, name='serveOramap'),
    path('maps/<int:map_id>/oramap/<str:sync>/', views.serveOramap, name='serverSyncOramap'),
    path('maps/<int:map_id>/delete/', views.DeleteMap, name='DeleteMap'),
    # path(r'^maps/(?P<arg>\d+)/setdownloadingstatus/?$', views.SetDownloadingStatus, name='SetDownloadingStatus'),
    # path(r'^maps/(?P<arg>\d+)/add(?P<item>\w+)sc/?$', views.addScreenshot, name='addScreenshot'),
    # path(r'^maps/(?P<arg>\d+)/revisions/?$', views.maps_revisions, name='maps_revisions'),
    # path(r'^maps/(?P<arg>\d+)/revisions/page/(?P<page>\d+)/?$', views.maps_revisions, name='maps_revisions'),
    # path(r'^maps/(?P<arg>\d+)/update/?$', views.updateMap, name='updateMap'),
    # path(r'^maps/(?P<arg>\d+)/update_logs/?$', views.updateMapLogs, name='updateMapLogs'),
    # path(r'^(?P<item_type>\w+)/(?P<arg>\d+)/unsubscribe/?$', views.unsubscribe_from_comments, name='Unsubscribe from comments to item'),
    # path(r'^maps/author/(?P<author>.+?)/page/(?P<page>\d+)/?$', views.maps_author, name='maps_author'),
    # path(r'^maps/author/(?P<author>.+?)/?$', views.maps_author, name='maps_author'),
    # path(r'^maps/uploader/(?P<arg>\d+)/?$', views.maps_uploader, name='maps_uploader'),
    # path(r'^maps/uploader/(?P<arg>\d+)/page/(?P<page>\d+)/?$', views.maps_uploader, name='maps_uploader'),
    # path(r'^maps/duplicates/(?P<maphash>[^/]+)/?$', views.maps_duplicates, name='maps_duplicates'),
    # path(r'^maps/duplicates/(?P<maphash>[^/]+)/page/(?P<page>\d+)/?$', views.maps_duplicates, name='maps_duplicates'),
    # path(r'^maps/page/(?P<page>\d+)/?$', views.maps, name='maps_paged'),
    path('maps/<int:map_id>/yaml/', views.serveYaml, name='printYaml'),
    # path(r'^maps/(?P<arg>\d+)/rules/?$', views.serveYamlRules, name='printYamlRules'),
    # path(r'^maps/(?P<arg>\d+)/lua/(?P<name>[^/]+)/?$', views.serveLua, name='printLua'),

    # path(r'^upload/map/?$', views.uploadMap, name='uploadMap'),
    # path(r'^upload/map/(?P<previous_rev>\d+)/?$', views.uploadMap, name='uploadMap'),


    # path(r'^screenshots/?$', views.screenshots, name='screenshots'),
    # path(r'^screenshots/(?P<itemid>\d+)/?$', views.serveScreenshot, name='serveScreenshot'),
    # path(r'^screenshots/(?P<itemid>\d+)/delete/?$', views.deleteScreenshot, name='deleteScreenshot'),
    # path(r'^screenshots/(?P<itemid>\d+)/(?P<itemname>\w+)/?$', views.serveScreenshot, name='serveScreenshot'),

    # path(r'^comments/?$', views.comments, name='comments'),
    # path(r'^comments/page/(?P<page>\d+)/?$', views.comments, name='comments_paged'),
    # path(r'^comments/user/(?P<arg>\d+)/?$', views.comments_by_user, name='comments_by_user'),
    # path(r'^comments/user/(?P<arg>\d+)/page/(?P<page>\d+)/?$', views.comments_by_user, name='comments_by_user_paged'),


    path('<str:name>/<int:id>/cancelreport/', views.cancelReport, name='cancelReport'),

    # path(r'^deletecomment/(?P<arg>\d+)/(?P<item_type>\w+)/(?P<item_id>\w+)/?$', views.deleteComment, name='deleteComment'),

    # path(r'^auth/register/?$', RegistrationView.as_view(form_class=RegistrationFormUniqueEmail), name='registration_register'),
    # path(r'^auth/', include('registration.backends.default.urls')),

    path('login/', views.loginView, name='loginView'),
    path('logout/', views.logoutView, name='logoutView'),

    # path(r'^accounts/', include('allauth.urls')),
    # path(r'^accounts/profile/?$', views.profile, name='profile'),


    # path(r'^news/feed.rss?$', views.feed, name='feed'),
    # path(r'^search/?$', views.search, name='search'),
    # path(r'^search/(?P<arg>.+?)/?$', views.search, name='search'),

    # path(r'^panel/?$', views.ControlPanel, name='ControlPanel'),
    # path(r'^panel/mymaps/?$', views.ControlPanel, name='ControlPanel'),
    # path(r'^panel/mymaps/page/(?P<page>\d+)/?$', views.ControlPanel, name='maps_paged'),
    # path(r'^panel/mymaps/page/(?P<page>\d+)/filter/(?P<filter>\w+)/?$', views.ControlPanel, name='maps_paged_filtered'),
    # path(r'^panel/mymaps/filter/(?P<filter>\w+)/?$', views.ControlPanel, name='maps_filtered'),

    # path(r'^faq/?$', views.faq, name='faq'),
    # path(r'^contacts/?$', views.contacts, name='contacts'),
    # path(r'^contacts/sent/?$', views.contacts_sent, name='contacts_sent'),

    # path(r'^map/', include([
    #     path(r'^hash/(?P<map_hashes>[^/]+)/yaml/?$', api.map_info_from_hashes, {'yaml': True}, name='mapAPI'),
    #     path(r'^hash/(?P<map_hashes>[^/]+)/?$', api.map_info_from_hashes, name='mapAPI'),
    #     path(r'^id/(?P<map_ids>[^/]+)/yaml/?$', api.map_info_from_ids, {'yaml': True}, name='mapAPI'),
    #     path(r'^id/(?P<map_ids>[^/]+)/?$', api.map_info_from_ids, name='mapAPI'),
    #     path(r'^url/(?P<map_hashes>[^/]+)/yaml/?$', api.map_urlinfo_from_hashes, {'yaml': True}, name='mapAPI'),
    #     path(r'^url/(?P<map_hashes>[^/]+)/?$', api.map_urlinfo_from_hashes, name='mapAPI'),
    #     path(r'^lastmap/yaml/?$', api.latest_map_info, {'yaml': True}, name='mapAPI'),
    #     path(r'^lastmap/?$', api.latest_map_info, name='mapAPI'),
    #     path(r'^(?P<map_hash>\w+)/?$', api.download_map, name='mapAPI_download'),
    # ])),

    # path(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    # path(r'^robots.txt$', views.robots, name='robots.txt'),

    path('ajax/jRating/<str:item_type>/', ajax.jRating, name='ajax.jRating'),

    # path(r'^.*$', views.handle404, name='handle404'),
]
