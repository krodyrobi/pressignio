from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext

import datetime

from blog.forms import LoginForm, RegisterForm
from blog.models import Article, Author

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))

def register_user(request):
	username = request.POST['username']
	password = request.POST['password']
	pass_check = request.POST['pass_check']
	author_name = request.POST['author_name']

	email = request.POST['email']

	login_date_time = datetime.datetime.now()

	user = Users.object.create_user('', '', '')
	user.save()

def login_user(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			user = authenticate(username=form.cleaned_data['username'],
				password=form.cleaned_data['password'])
			if user is not None:
				login(request, user)

				latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
				return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))

			else:
				return render_to_response('blog/login.html', {'is_good': False, 'form': form},
					context_instance=RequestContext(request))
		else:
			return render_to_response('blog/login.html', {'is_good': True, 'form': form},
					context_instance=RequestContext(request))
	else:
		form = LoginForm()
		return render_to_response('blog/login.html', {'is_good': True, 'form': form},
			context_instance=RequestContext(request))

def logout_user(request):
	logout(request)

	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]

	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))

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
