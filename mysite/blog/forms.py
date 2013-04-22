from django import forms
from django.forms import ModelForm

from blog.models import Article

import datetime		

class RegisterForm(forms.Form):
    	username = forms.CharField(max_length=30)
    	password = forms.CharField(widget=forms.PasswordInput)
	pass_check = forms.CharField(widget=forms.PasswordInput)

	author_name = forms.CharField(max_length=100)
	author_description = forms.CharField(widget=forms.Textarea)

	email = forms.EmailField()

class LoginForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)

class ArticleForm(ModelForm):
	class Meta:
		model = Article
		exclude = ('slug', 'publication_date',)

class EditForm(forms.Form):
	pk = forms.IntegerField()

class DeleteForm(forms.Form):
	pk = forms.IntegerField()
	page = forms.IntegerField()
