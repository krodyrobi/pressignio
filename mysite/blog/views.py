from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Q

from blog.forms import LoginForm, RegisterForm, ArticleForm, EditForm, DeleteForm, AccountForm, EmailResendForm, ResetPasswordForm, sendValidationEmail, sendRetrievePasswordEmail
from blog.models import Article, Author

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
				user,author = form.save()
				sendValidationEmail(user,author)
				message = ' Account has been created, to complete the registration process go to the link sent to your email adress (%s)' %(data['email'])
				request.session['message'] = message
				
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
			message_error = ' Wrong activation link. Try again!'
			request.session['message_error'] = message_error
			return redirect(reverse('login_user'))

		user.is_active = True
		user.save()
		
		message = ' Account succesfully activated.'
		request.session['message'] = message
		
		return redirect(reverse('login_user'))
				
	else:
		
		return redirect(reverse('index'))

def resetPassword(request):
	if request.user.is_anonymous():
		if request.method == 'POST':
			form = ResetPasswordForm(request.POST)
		
			if form.is_valid():
				user = User.objects.get(Q(email=form.cleaned_data['username_email']) | Q(username=form.cleaned_data['username_email']))
				form.send(user)
			
				return render_to_response('blog/reset_password.html', {'form': form, 'is_good': True}, context_instance=RequestContext(request))
			else:
				return render_to_response('blog/reset_password.html', {'form': form}, context_instance=RequestContext(request))
		else:
			form = ResetPasswordForm()
			return render_to_response('blog/reset_password.html', {'form': form}, context_instance=RequestContext(request))
	else:
		raise Http404
		
def passwordRecovery(request, username, recovery_code):
	if request.user.is_anonymous():
		if request.method == 'GET':
			try:
					user = User.objects.get(username = username, author__recovery_code = recovery_code)
			except ObjectDoesNotExist:
				message_error = ' Wrong recovery link. Try again!'
				request.session['message_error'] = message_error
				return redirect(reverse('login_user'))
			else:
				sendRetrievePasswordEmail(user)
				message = ' Password reset successfull check your email for the new password. (%s)' % (user.email)
				request.session['message'] = message
				return redirect(reverse('login_user'))
		else:
			raise Http404
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
		message = None
		message_error = None
		
		if 'message' in request.session:
			message = request.session['message']
			del request.session['message']
		if 'message_error' in request.session:
			message_error = request.session['message_error']
			del request.session['message_error']
		
		if message or message_error:			
			return render_to_response('blog/login.html', {'is_good': [True,True], 'form': form, 'message': message, 'message_error': message_error},
				context_instance=RequestContext(request))
		else:	
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
				instance=Article(title='', text='', author=request.user.author, publication_date=datetime.datetime.now())
				instance.save()
				form = ArticleForm(instance=Article())

				return render_to_response('blog/edit_one_article.html', {'article_pk': instance.pk, 'form': form, 'is_good': is_good}, 
					context_instance=RequestContext(request))
		else:
			try:
				article = Article.objects.get(pk=article_pk)

				form = ArticleForm(instance=article)
			except ObjectDoesNotExist:
				form = ArticleForm()

			return render_to_response('blog/edit_one_article.html', {'article_pk': article_pk, 'form': form, 'is_good': is_good}, 
				context_instance=RequestContext(request))
