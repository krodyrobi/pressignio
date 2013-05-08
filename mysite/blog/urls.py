from django.conf.urls import patterns, url

from blog import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<title_slug>[-\w]+)/$', views.detail, name='detail'),
	url(r'^login/$', views.login_user, name='login_user'),
	url(r'^logout/$', views.logout_user, name='logout_user'),
	url(r'^register/$', views.registerUser, name='registerUser'),
	url(r'^resend/$', views.resendEmailValidation, name='resendEmailValidation'),
	url(r'^confirm/(?P<confirmation_code>[-\w]+)/$', views.confirm, name='confirm'),
	url(r'^reset_password/$', views.resetPassword, name='resetPassword'),
	url(r'^passwordRecovery/(?P<recovery_code>[-\w]+)/$', views.passwordRecovery, name='passwordRecovery'),
	url(r'^myaccount/$', views.edit_account, name='edit_account'),
	url(r'^myarticles/$', views.edit_articles, name='edit_articles'),
	url(r'^myarticles/page/(?P<page>\d+)/$', views.edit_articles, name='edit_articles'),
	url(r'^myarticles/edit/$', views.edit, name='edit'),
	url(r'^myarticles/delete/$', views.delete, name='delete'),
	url(r'^myarticles/edit/(?P<article_pk>\d+)/$', views.edit_one_article, name='edit_one_article'),
	url(r'^(?P<name_slug>[-\w]+)/$', views.author, name='author'),
)
