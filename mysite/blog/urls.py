from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<title_slug>[-\w]+)/$', views.detail, name='detail'),
	url(r'^login/$', views.login_user, name='login_user'),
	url(r'^logout/$', views.logout_user, name='logout_user'),
	url(r'^register/$', views.registerUser, name='registerUser'),
	url(r'^confirm/(?P<confirmation_code>[-\w]+)/(?P<username>[-\w]+)/$', views.confirm, name='confirm'),
	url(r'^(?P<name_slug>[-\w]+)/$', views.author, name='author'),
)
