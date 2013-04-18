from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse

import datetime

from blog.forms import RegisterForm
from blog.models import Article, Author

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list})

def registerUser(request):
	if request.method == 'POST':	
		login_date_time = datetime.datetime.now()
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.clean()
			user = User.objects.create_user(form['username'], form['email'], form['password'])
			author = Author.objects.create_author(user = user, name = form['author_name'], description = form['author_description'])
			user.save()
			author.save() 
			return render_ro_response('blog/register_ok.html', {'form': form},context_instance=RequestContext(request))

		else:
			return HttpResponse("error form is invalid", content_type="text/plain")
			
				###### Continue form errors ######
	else:
		return render_to_response('blog/register.html', context_instance=RequestContext(request))
	

def detail(request, title_slug, year, month):
	article = get_object_or_404(Article, slug=title_slug, publication_date__year=year,
		publication_date__month=month)
	return render_to_response('blog/detail.html', {'article': article})

def author(request, name_slug):
	author = get_object_or_404(Author, slug=name_slug)
	latest_articles_list = Article.objects.filter(author=author).order_by('-publication_date')[:3]
	return render_to_response('blog/author.html', {'author': author,
		'latest_articles_list': latest_articles_list})
