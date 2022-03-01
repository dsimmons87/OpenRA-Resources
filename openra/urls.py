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
    path('maps/<int:map_id>/setdownloadingstatus/', views.SetDownloadingStatus, name='SetDownloadingStatus'),
    path('maps/<int:id>/add<str:item>sc/', views.addScreenshot, name='addScreenshot'),
    path('maps/<int:map_id>/revisions/', views.maps_revisions, name='maps_revisions'),
    path('maps/<int:map_id>/revisions/page/<int:page>/', views.maps_revisions, name='maps_revisions'),
    # path(r'^maps/(?P<arg>\d+)/update/?$', views.updateMap, name='updateMap'),
    # path(r'^maps/(?P<arg>\d+)/update_logs/?$', views.updateMapLogs, name='updateMapLogs'),
    # path(r'^(?P<item_type>\w+)/(?P<arg>\d+)/unsubscribe/?$', views.unsubscribe_from_comments, name='Unsubscribe from comments to item'),
    path('maps/author/<str:author>/page/<int:page>/', views.maps_author, name='maps_author'),
    path('maps/author/<str:author>/', views.maps_author, name='maps_author'),
    # path(r'^maps/uploader/(?P<arg>\d+)/?$', views.maps_uploader, name='maps_uploader'),
    # path(r'^maps/uploader/(?P<arg>\d+)/page/(?P<page>\d+)/?$', views.maps_uploader, name='maps_uploader'),
    # path(r'^maps/duplicates/(?P<maphash>[^/]+)/?$', views.maps_duplicates, name='maps_duplicates'),
    # path(r'^maps/duplicates/(?P<maphash>[^/]+)/page/(?P<page>\d+)/?$', views.maps_duplicates, name='maps_duplicates'),
    path('maps/page/<int:page>/', views.maps, name='maps_paged'),
    path('maps/<int:map_id>/yaml/', views.serveYaml, name='printYaml'),
    path('maps/<int:map_id>/rules/', views.serveYamlRules, name='printYamlRules'),
    path('maps/<int:map_id>/lua/<str:filename>/', views.serveLua, name='printLua'),

    path('upload/map/', views.uploadMap, name='uploadMap'),
    path('upload/map/<int:previous_rev>/', views.uploadMap, name='uploadMap'),

    path('screenshots/<int:screenshot_id>/', views.serveScreenshot, name='serveScreenshot'),
    path('screenshots/<int:screenshot_id>/delete/', views.deleteScreenshot, name='deleteScreenshot'),
    path('screenshots/<int:screenshot_id>/<str:itemname>/', views.serveScreenshot, name='serveScreenshot'),

    path('comments/', views.comments, name='comments'),
    path('comments/page/<int:page>/', views.comments, name='comments_paged'),
    path('comments/user/<int:user_id>/', views.comments_by_user, name='comments_by_user'),
    path('comments/user/<int:user_id>/page/<int:page>/', views.comments_by_user, name='comments_by_user_paged'),


    path('<str:name>/<int:id>/cancelreport/', views.cancelReport, name='cancelReport'),

    path('deletecomment/<int:comment_id>/<str:item_type>/<int:item_id>/', views.deleteComment, name='deleteComment'),

    # path(r'^auth/register/?$', RegistrationView.as_view(form_class=RegistrationFormUniqueEmail), name='registration_register'),
    # path(r'^auth/', include('registration.backends.default.urls')),

    path('login/', views.loginView, name='loginView'),
    path('logout/', views.logoutView, name='logoutView'),

    # path(r'^accounts/', include('allauth.urls')),
    path('accounts/profile/', views.profile, name='profile'),


    path('news/feed.rss', views.feed, name='feed'),
    path('search/', views.search, name='search'),
    path('search/<str:search_request>/', views.search, name='search'),

    path('panel/', views.ControlPanel, name='ControlPanel'),
    path('panel/mymaps/', views.ControlPanel, name='ControlPanel'),
    path('panel/mymaps/page/<int:page>/', views.ControlPanel, name='maps_paged'),

    path('faq/', views.faq, name='faq'),
    path('contacts/', views.contacts, name='contacts'),
    path('contacts/sent/', views.contacts_sent, name='contacts_sent'),

    path('map/', include([
        path('hash/<str:map_hashes>/yaml/', api.map_info_from_hashes, {'yaml': True}, name='mapAPI'),
        path('hash/<str:map_hashes>/', api.map_info_from_hashes, name='mapAPI'),
        path('id/<str:map_ids>/yaml/', api.map_info_from_ids, {'yaml': True}, name='mapAPI'),
        path('id/<str:map_ids>/', api.map_info_from_ids, name='mapAPI'),
        path('url/<str:map_hashes>/yaml/', api.map_urlinfo_from_hashes, {'yaml': True}, name='mapAPI'),
        path('url/<str:map_hashes>/', api.map_urlinfo_from_hashes, name='mapAPI'),
        path('lastmap/yaml/', api.latest_map_info, {'yaml': True}, name='mapAPI'),
        path('lastmap/', api.latest_map_info, name='mapAPI'),
        path('<str:map_hash>/', api.download_map, name='mapAPI_download'),
    ])),

    path('favicon.ico', views.favicon, name='favicon'),
    path('robots.txt', views.robots, name='robots.txt'),

    path('ajax/jRating/<str:item_type>/', ajax.jRating, name='ajax.jRating'),

    # path(r'^.*$', views.handle404, name='handle404'),
]
