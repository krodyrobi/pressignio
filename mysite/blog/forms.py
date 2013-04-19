from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django import forms

import datetime	

from blog.models import Author	

class RegisterForm(forms.Form):
    	username = forms.CharField(max_length=30)
    	password = forms.CharField(widget=forms.PasswordInput)
	pass_check = forms.CharField(widget=forms.PasswordInput)

	author_name = forms.CharField(max_length=100)
	author_description = forms.CharField(widget=forms.Textarea)

	email = forms.EmailField()


	def clean(self):
		cleaned_data = self.cleaned_data
		
		password1 = cleaned_data.get("password")
		password2 = cleaned_data.get("pass_check")


		if password1 != password2:
			raise forms.ValidationError("Passwords must be identical!")
		
		if len(password1) < 6 :
			raise forms.ValidationError("Password must be at least 6 characters long!")
		
		try:
			check = User.objects.get(username=cleaned_data['username'])

		except ObjectDoesNotExist:

			user = User.objects.create_user(cleaned_data['username'], cleaned_data['email'], cleaned_data['password'])
			user.is_active = False
			author = Author(user = user, name = cleaned_data['author_name'], description = cleaned_data['author_description'])
			user.save()
			author.save()

		else:
			raise forms.ValidationError("Username already exists, please choose another one!")

		return cleaned_data

class LoginForm(forms.Form):
	username = forms.CharField(max_length=30)
	password = forms.CharField(widget=forms.PasswordInput)
