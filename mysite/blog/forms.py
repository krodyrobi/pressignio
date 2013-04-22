from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

from blog.models import Article

import string 
import datetime
import random

from blog.models import Author	

class RegisterForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(label="Password",widget=forms.PasswordInput,min_length=6)
	pass_check = forms.CharField(label="Re-type password",widget=forms.PasswordInput)

	author_name = forms.CharField(max_length=100)
	author_description = forms.CharField(label="Description",widget=forms.Textarea)

	email = forms.EmailField()

	def __init__(self, *args, **kwargs):
		super(RegisterForm, self).__init__(*args, **kwargs)


		for field in self.fields.values():
		    field.error_messages = {'required':'The field {fieldname} is required!'.format(fieldname=field.label)}


	def clean(self):
		cleaned_data = super(RegisterForm, self).clean()
		
		try:
			check = User.objects.get(username=cleaned_data['username'])
			
		except ObjectDoesNotExist:
			pass
		else:
			raise forms.ValidationError("Username already exists, please choose another one!")
		
		try:
			check = User.objects.get(email=cleaned_data['email'])
		except ObjectDoesNotExist:
			pass
		else:
			raise forms.ValidationError("Email already taken, please choose another one!")
		
		password1 = cleaned_data.get("password")
		password2 = cleaned_data.get("pass_check")

		if password1 != password2:
			raise forms.ValidationError("Passwords must match!")
		
	
		return cleaned_data

	def save(self):
		cleaned_data = self.cleaned_data
		
		user = User.objects.create_user(username = cleaned_data['username'], email = cleaned_data['email'], password = cleaned_data['password'])
		user.is_active = False
		
		code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(35))
		author = Author(user = user, name = cleaned_data['author_name'], description = cleaned_data['author_description'], confirmation_code = code)
		user.save()
		author.save()

		return user,author

		
	def sendValidationEmail(self , user, author):

		title = "Pressignio account confirmation:"
		content = "localhost:8000/blog/confirm/" + str(author.confirmation_code) + "/" + user.username
		send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)		
	
class LoginForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)

class ArticleForm(ModelForm):
	class Meta:
		model = Article
		exclude = ('slug', 'publication_date', 'author')

class EditForm(forms.Form):
	pk = forms.IntegerField()

class DeleteForm(forms.Form):
	pk = forms.IntegerField()
	page = forms.IntegerField()
