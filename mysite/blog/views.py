from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


import datetime


from blog.models import Article

def index(request):
	latest_articles_list = Article.objects.all().order_by('-publication_date')[:10]
	return render_to_response('blog/index.html', {'latest_articles_list': latest_articles_list})



def index_register(request):
	return render_to_response('blog/register.html')

def register_user(request):
	username = request.POST['username']
	password = request.POST['password']
	first_name = request.POST['first_name']
	last_name = request.POST['last_name']
	email = request.POST['email']

	login_date_time = datetime.datetime.now()

	user = Users.object.create_user('', '', '')
	user.save()


    

	
