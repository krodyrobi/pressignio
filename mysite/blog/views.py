from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.http import require_POST

from blog.forms import LoginForm, RegisterForm, ArticleForm, EditForm, DeleteForm, AccountForm, EmailResendForm, ResetPasswordForm, sendValidationEmail, sendRetrievePasswordEmail
from blog.models import Article, UserProfile

import datetime

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))
		
def registerUser(request):
	if request.user.is_anonymous():
		if request.method == 'POST':	
			form = RegisterForm(request.POST)
			
			if form.is_valid():
				data = form.cleaned_data
				author = form.save()
				sendValidationEmail(author)
				message = 'Account has been created, to complete the registration process go to the link sent to your email adress (%s)' %(data['email'])
				messages.add_message(request, messages.INFO, message)
				
				return redirect(reverse('login_user'))
			else: 
				return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))
		else:
				form = 	RegisterForm()	
				return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))
	else:
		raise Http404

def resendEmailValidation(request):
	if request.method == 'POST':
		form = EmailResendForm(request.POST)
		if form.is_valid():
			author = UserProfile.objects.get(user__email = form.cleaned_data['email'])

			form.resend(author)
			
			message = 'Email resent.'
			messages.add_message(request, messages.INFO, message)
			return render_to_response('blog/resend_email.html', {'form': form}, context_instance=RequestContext(request))
		else:
			message = 'Either user is already active or link is invalid.'
			messages.add_message(request, messages.ERROR, message)
			return render_to_response('blog/resend_email.html', {'form': form}, context_instance=RequestContext(request))
	else:
		form = 	EmailResendForm()	
		return render_to_response('blog/resend_email.html', {'form': form}, context_instance=RequestContext(request))

		
def confirm(request, confirmation_code):
	try:
		author = UserProfile.objects.get(confirmation_code = confirmation_code, user__is_active = False)
	except UserProfile.DoesNotExist:
		message = 'Wrong activation link. Try again.'
		messages.add_message(request, messages.ERROR, message)
		return redirect(reverse('login_user'))

	author.user.is_active = True
	author.user.save()
	
	message = 'Account succesfully activated.'
	messages.add_message(request, messages.INFO, message)
	
	return redirect(reverse('login_user'))

def resetPassword(request):
	if request.user.is_anonymous():
		if request.method == 'POST':
			form = ResetPasswordForm(request.POST)
		
			if form.is_valid():
				user = User.objects.get(Q(email=form.cleaned_data['username_email']) | Q(username=form.cleaned_data['username_email']))
				form.send(user)
			
				message = 'Password recovery email sent.'
				messages.add_message(request, messages.INFO, message)
				return render_to_response('blog/reset_password.html', {'form': form}, context_instance=RequestContext(request))
			else:
				return render_to_response('blog/reset_password.html', {'form': form}, context_instance=RequestContext(request))
		else:
			form = ResetPasswordForm()
			return render_to_response('blog/reset_password.html', {'form': form}, context_instance=RequestContext(request))
	else:
		raise Http404
		
def passwordRecovery(request, recovery_code):
	if request.user.is_anonymous():
		try:
			author = UserProfile.objects.get(recovery_code = recovery_code)
		except UserProfile.DoesNotExist:
			message = 'Wrong recovery link. Try again!'
			messages.add_message(request, messages.ERROR, message)
			return redirect(reverse('login_user'))
		else:
			sendRetrievePasswordEmail(author.user)
			message = 'Check your email for the reset link. (%s)' % (author.user.email)
			messages.add_message(request, messages.INFO, message) 
			return redirect(reverse('login_user'))
	else:
		raise Http404
		
def login_user(request):
	if request.user.is_anonymous():
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
						messages.add_message(request, messages.ERROR, 
							'''Account not activated yet, check your
							 email for the validation link. <a href="
							/blog/resend/">Not there? Resend it here!</a>''')

						return render_to_response('blog/login.html', {'form': form},
						context_instance=RequestContext(request))
				else:
					messages.add_message(request, messages.ERROR, 
					'Wrong username or password.') 

					return render_to_response('blog/login.html', {'form': form},
						context_instance=RequestContext(request))
			else:
				return render_to_response('blog/login.html', {'form': form},
						context_instance=RequestContext(request))
		else:
			form = LoginForm()
		
			return render_to_response('blog/login.html', {'form': form},
				context_instance=RequestContext(request))
	else:
		return redirect(reverse('index'))

@login_required			
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

@login_required
def edit_account(request):
	user = request.user

	if request.method == 'POST':
		form = AccountForm(request.POST, instance=user.get_profile())

		if form.is_valid():
			form.save()
			
			messages.add_message(request, messages.INFO, 
			'Your edits have been saved successfully.')

		return render_to_response('blog/edit_account.html', 
			{'form': form},
			context_instance=RequestContext(request))
	else:
		author = user.get_profile()
		form = AccountForm(instance=user.get_profile(), initial={'name': author.name,
			'description': author.description})

		return render_to_response('blog/edit_account.html', 
			{'form': form},
			context_instance=RequestContext(request))

@login_required
def edit_articles(request, page=1):
	author = request.user.get_profile()
	latest_articles_list = []
	page = int(page) + 1
	while not latest_articles_list and page > 1:
		page = int(page) - 1
		latest_articles_list = Article.objects.filter(author=author)
		latest_articles_list.order_by('-publication_date')[5 * (int(page) - 1) : 5 * int(page)]
	last = Article.objects.filter(author=author).count() <= 5 * int(page)
	return render_to_response('blog/edit_articles.html', 
		{'latest_articles_list': latest_articles_list,
		'page': int(page), 'last': last}, context_instance=RequestContext(request))

@login_required
@require_POST
def edit(request):
	form = EditForm(request.POST)

	if form.is_valid():
		try:
			article_pk = form.cleaned_data['pk']

			article = Article.objects.get(pk=article_pk, 
				author=request.user.get_profile())
			form = ArticleForm(instance=article)
			return render_to_response('blog/edit_one_article.html', 
				{'article_pk': article_pk, 'form': form, 'is_good': False}, 
				context_instance=RequestContext(request))
		except Article.DoesNotExist:
			return render_to_response('blog/edit_one_article.html', 
				{'article_pk': 0, 'is_good': False}, 
				context_instance=RequestContext(request))

	else:
		return HttpResponseForbidden()

@login_required
@require_POST
def delete(request):
	form = DeleteForm(request.POST)

	if form.is_valid():
		try:
			article_pk = form.cleaned_data['pk']

			article = Article.objects.get(pk=article_pk, 
				author=request.user.author)
			article.delete()
		except Article.DoesNotExist:
			return HttpResponseForbidden()

		return redirect(reverse('edit_articles', 
			args=(form.cleaned_data['page'],)))

	else:
		return HttpResponseForbidden()

@login_required
def edit_one_article(request, article_pk=0):
	try:
		article = Article.objects.get(pk=article_pk, author=request.user.get_profile())
	except Article.DoesNotExist:
		article = None
	if request.method == 'POST':
		form = ArticleForm(request.POST, instance=article)
		if form.is_valid():
			art = form.save(commit=False)
			art.author = request.user.get_profile()
			art.save()

		messages.add_message(request, messages.INFO, 
			'Your edits have been saved successfully.')

		return render_to_response('blog/edit_one_article.html', 
			{'article_pk': article_pk, 'form': form}, 
			context_instance=RequestContext(request))
	else:
		try:
			article = Article.objects.get(pk=article_pk, author=request.user.get_profile())
		except Article.DoesNotExist:	
			form = ArticleForm()

		return render_to_response('blog/edit_one_article.html', 
			{'article_pk': article_pk, 'form': form}, 
			context_instance=RequestContext(request))
