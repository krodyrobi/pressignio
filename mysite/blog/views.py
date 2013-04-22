from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext

from blog.forms import LoginForm, RegisterForm
from blog.models import Article, Author

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list}, context_instance=RequestContext(request))
		
def registerUser(request):
	
	if request.method == 'POST':	
		form = RegisterForm(request.POST)

		if form.is_valid():
			data = form.cleaned_data
			user , author = form.save()
			form.sendValidationEmail(user,author)	
						
			return render_to_response('blog/register_ok.html', {'author': data},context_instance=RequestContext(request))
		else: 
			return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))
			
		#######FINISH email registration #########
	else:
		form = RegisterForm()
		return render_to_response('blog/register.html', {'form': form}, context_instance=RequestContext(request))

def confirm(request, username, confirmation_code):
	if request.method == 'GET':	

		try:
			user = User.objects.get(username = username, author__confirmation_code = confirmation_code, is_active = False)
		except ObjectDoesNotExist:
			raise Http404

		user.is_active = True
		user.save()

		return redirect(reverse('index'))
				
	else:
		return redirect(reverse('index'))















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
