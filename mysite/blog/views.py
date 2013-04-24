from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse

from blog.forms import LoginForm, RegisterForm, ArticleForm, EditForm, DeleteForm, AccountForm, EmailResendForm, RetrievePasswordForm
from blog.models import Article, Author

import datetime

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))
		
def registerUser(request):
	if request.method == 'POST':	
		form = RegisterForm(request.POST)

		if form.is_valid():
			data = form.cleaned_data
			user,author = form.save()
			form.sendValidationEmail(user,author)	
						
			return render_to_response('blog/register_ok.html', {'author': data},context_instance=RequestContext(request))
		else: 
			return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))
	else:
			form = 	RegisterForm()	
			return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))

def resendEmailValidation(request):
	if request.method == 'POST':
		form = EmailResendForm(request.POST)
		if form.is_valid():
			author = Author.objects.get(user__email = form.cleaned_data['email'])
			user = User.objects.get(id = author.user_id)

			form.resend(user, author)
			return render_to_response('blog/resend_email.html', {'form': form, 'is_good': True}, context_instance=RequestContext(request))
		else:
			return render_to_response('blog/resend_email.html', {'form': form, 'error': True}, context_instance=RequestContext(request))
	else:
		form = 	EmailResendForm()	
		return render_to_response('blog/resend_email.html', {'form': form}, context_instance=RequestContext(request))

		
def confirm(request, username, confirmation_code):
	if request.method == 'GET':

		try:
			user = User.objects.get(username = username, author__confirmation_code = confirmation_code, is_active = False)
		except ObjectDoesNotExist:
			raise Http404

		user.is_active = True
		user.save()

		return redirect(reverse('login_user'))
				
	else:
		return redirect(reverse('index'))

def retriveLostPassword(request):
	if request.user.is_anonymous():
		if request.method == 'POST':
			form = RetrievePasswordForm(request.POST)
		
			if form.is_valid():
				user = User.objects.get(email = form.cleaned_data['email'])
				form.send(user)
			
				return render_to_response('blog/retrieve_password.html', {'form': form, 'is_good': True}, context_instance=RequestContext(request))
			else:
				return render_to_response('blog/retrieve_password.html', {'form': form}, context_instance=RequestContext(request))
		else:
			form = RetrievePasswordForm()
			return render_to_response('blog/retrieve_password.html', {'form': form}, context_instance=RequestContext(request))
	else:
		raise Http404
		
def login_user(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			user = authenticate(username=form.cleaned_data['username'],
				password=form.cleaned_data['password'])
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect(reverse('index'))
				else:
					return render_to_response('blog/login.html', {'is_good': [True,False], 'form': form},
					context_instance=RequestContext(request))
			else:
				return render_to_response('blog/login.html', {'is_good': [False,True], 'form': form},
					context_instance=RequestContext(request))
		else:
			return render_to_response('blog/login.html', {'is_good': [False,True], 'form': form},
					context_instance=RequestContext(request))
	else:
		form = LoginForm()
		return render_to_response('blog/login.html', {'is_good': [True,True], 'form': form},
			context_instance=RequestContext(request))

def logout_user(request):
	logout(request)

	return redirect(reverse('index'))

def detail(request, title_slug, year, month):
	article = get_object_or_404(Article, slug=title_slug, publication_date__year=year,
		publication_date__month=month)
	return render_to_response('blog/detail.html', {'article': article},
		context_instance=RequestContext(request))

def author(request, name_slug):
	author = get_object_or_404(Author, slug=name_slug)
	latest_articles_list = Article.objects.filter(author=author).order_by('-publication_date')[:3]
	return render_to_response('blog/author.html', {'author': author,
		'latest_articles_list': latest_articles_list},
		context_instance=RequestContext(request))

def edit_account(request):
	is_good = False

	if request.user.is_anonymous():
		raise Http404
	else:
		
		user = request.user

		if request.method == 'POST':
			form = AccountForm(request.POST, instance=user)

			if form.is_valid():
				is_good = True

				form.save()

				return render_to_response('blog/edit_account.html', {'is_good': is_good, 'form': form},
					context_instance=RequestContext(request))
		else:
			form = AccountForm(instance=user, initial={'author_name': user.author.name,
				'author_description': user.author.description})

			return render_to_response('blog/edit_account.html', {'is_good': is_good, 'form': form},
					context_instance=RequestContext(request))

def edit_articles(request, page=1):
	if request.user.is_anonymous():
		raise Http404
	else:
		author = request.user.author
		latest_articles_list = Article.objects.filter(author=author).order_by('-publication_date')[5 * (int(page) - 1) : 5 * int(page)]
		last = Article.objects.filter(author=author).count() <= 5 * int(page)
		return render_to_response('blog/edit_articles.html', {'latest_articles_list': latest_articles_list,
			'page': int(page), 'last': last}, context_instance=RequestContext(request))

def edit(request):
	if request.user.is_anonymous():
		raise Http404
	else:
		if request.method == 'POST':
			form = EditForm(request.POST)

			if form.is_valid():
				try:
					article_pk = form.cleaned_data['pk']

					article = Article.objects.get(pk=article_pk)
					form = ArticleForm(instance=article)

					return render_to_response('blog/edit_one_article.html', {'article_pk': article_pk, 'form': form, 'is_good': False}, 
					context_instance=RequestContext(request))
				except ObjectDoesNotExist:
					return edit_one_article(request)

			else:
				raise Http404
		else:
			raise Http404

def delete(request):
	if request.user.is_anonymous():
		raise Http404
	else:
		if request.method == 'POST':
			form = DeleteForm(request.POST)

			if form.is_valid():
				try:
					article_pk = form.cleaned_data['pk']

					article = Article.objects.get(pk=article_pk)
					article.delete()
				except ObjectDoesNotExist:
					raise Http404

				return redirect(reverse('edit_articles', args=(form.cleaned_data['page'],)))

			else:
				raise Http404
		else:
			raise Http404

def edit_one_article(request, article_pk=0):
	is_good = False

	if request.user.is_anonymous():
		raise Http404
	else:
		if request.method == 'POST':
			try:
				article = Article.objects.get(pk=article_pk)
				form = ArticleForm(request.POST, instance=article)

				if form.is_valid():
					is_good = True

					art = form.save(commit=False)
					art.publication_date = datetime.datetime.now()
					art.author = request.user.author
					art.save()

				return render_to_response('blog/edit_one_article.html', {'article_pk': article_pk, 'form': form, 'is_good': is_good}, 
					context_instance=RequestContext(request))
			except ObjectDoesNotExist:
				form = ArticleForm(request.POST)

				if form.is_valid():
					is_good = True

					art = form.save(commit=False)
					art.publication_date = datetime.datetime.now()
					art.author = request.user.author
					art.save()
					article_pk = art.pk

				return render_to_response('blog/edit_one_article.html', {'article_pk': article_pk, 'form': form, 'is_good': is_good}, 
					context_instance=RequestContext(request))
		else:
			try:
				article = Article.objects.get(pk=article_pk)

				form = ArticleForm(instance=article)
			except ObjectDoesNotExist:
				form = ArticleForm(request.POST)

			return render_to_response('blog/edit_one_article.html', {'article_pk': article_pk, 'form': form, 'is_good': is_good}, 
				context_instance=RequestContext(request))
