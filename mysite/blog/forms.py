from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm, ValidationError
from django.forms.util import ErrorList
from django.db.models import Q
from django.contrib.auth import authenticate


from blog.models import Article, UserProfile

import string 
import datetime
import random
import re


def sendValidationEmail(author):
	user = author.user
	title = "Pressignio account confirmation:"
	content = "localhost:8000/blog/confirm/%s/" % (author.confirmation_code)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)
	
def sendPasswordRecoveryConfirm(user):
	title = "Pressignio password recovery:"
	content = "localhost:8000/blog/passwordRecovery/%s/" % (user.get_profile().recovery_code)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)
	
def sendRetrievePasswordEmail(user):
	password = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(6))
	user.set_password(password)
	user.save()
	
	title = "Pressignio account password:"
	content = "Username:%s\nPassword:%s" % (user.username, password)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)

class RegisterForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ('user', 'slug', 'confirmation_code', 'recovery_code')
	
	username = forms.CharField(label='Username',max_length=30)
	password = forms.CharField(label='Password',widget=forms.PasswordInput, min_length=6)
	pass_check = forms.CharField(label='Re-type password',widget=forms.PasswordInput)
	email = forms.CharField(label='Email')
		
	def clean_username(self):
		username = self.cleaned_data['username']
		
		if re.search(r'[^a-z0-9\._]+', username):
			raise ValidationError('Illegal characters.')
			
		try:
			check = User.objects.get(username=username)
			
			raise ValidationError('Username already in use, choose another username.')
		except User.DoesNotExist:
			pass		
		
		return username

	def clean_email(self):
		email = self.cleaned_data['email']
		
		try:
			check = User.objects.get(email=email)
			
			raise ValidationError('Email already in use.')
		except User.DoesNotExist:
			pass
		
		return email
		
	def clean_name(self):
		name = self.cleaned_data['name']
		
		try:
			check = UserProfile.objects.get(name__iexact=self.cleaned_data['name'])
			
			raise ValidationError('This name has already been taken, please choose another.')
		except UserProfile.DoesNotExist:
			pass
	
		return name
		
	def clean(self):
		cleaned_data = super(RegisterForm, self).clean()
		
		password = cleaned_data.get("password")
		pass_check = cleaned_data.get("pass_check")

		if password != pass_check:
			if not self._errors.has_key('pass_check'):
				self._errors['pass_check'] = ErrorList()
				self._errors["pass_check"].append(u'Passwords must match!')
	
		return cleaned_data

	def save(self):
		cleaned_data = self.cleaned_data
		
		user = User.objects.create_user(username = cleaned_data['username'], email = cleaned_data['email'], password = cleaned_data['password'])
		user.is_active = False 
		
		code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(35))
		author = UserProfile.objects.create(user = user, name = cleaned_data['name'], description = cleaned_data['description'], confirmation_code = code)
		user.save()
		author.save()

		return author


class EmailResendForm(forms.Form):
	email = forms.EmailField()

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			check = UserProfile.objects.get(user__email=email, user__is_active=False)
		except UserProfile.DoesNotExist:
			if not self._errors.has_key('email'):
				self._errors['email'] = ErrorList()
				self._errors['email'].append(u'Email not found or user already active!')
			
		return email
    	
	def resend(self, author):
		sendValidationEmail(author)
		
class ResetPasswordForm(forms.Form):
	username_email = forms.CharField(max_length=30, label= "Username")
	
	def clean(self):
		cleaned_data = super(ResetPasswordForm, self).clean()
		
		try:
			if 'username_email' in cleaned_data:
				check = User.objects.get(Q(email=cleaned_data['username_email']) | Q(username=cleaned_data['username_email']) )
		except ObjectDoesNotExist:
				if not self._errors.has_key('username_email'):
					self._errors['username_email'] = ErrorList()
					self._errors['username_email'].append(u'No account with the email or username provided.')	
				
		return cleaned_data
		
	def send(self,user):
		author = user.get_profile()
		author.recovery_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(35))
		author.save()
		sendPasswordRecoveryConfirm(user)


class AccountForm(ModelForm):
	class Meta:
		model = UserProfile
		exclude = ('user', 'slug', 'confirmation_code', 'recovery_code')
	
	password = forms.CharField(label='Password',widget=forms.PasswordInput, min_length=6)
	
	newpass = forms.CharField(required=False, label='New password',widget=forms.PasswordInput, min_length=6)
	pass_check = forms.CharField(required=False, label='Re-type password',widget=forms.PasswordInput)
	
	def clean_name(self):
		name = self.cleaned_data['name']
		
		check = UserProfile.objects.filter(name__iexact=self.cleaned_data['name']).exclude(user__username = self.instance.user.username)
		
		if check:	
			raise ValidationError('This name has already been taken, please choose another.')
	
		return name
		
	def clean_password(self):
		password = self.cleaned_data['password']
		
		user = authenticate(username= self.instance.user.username, password= password)
		
		if user == None:
			raise ValidationError('Wrong password')
			
		return password

	def clean(self):
		cleaned_data = super(AccountForm, self).clean()

		password = cleaned_data.get("password")
		newpass = cleaned_data.get("newpass")
		pass_check = cleaned_data.get("pass_check")
		
		
		if newpass != pass_check and newpass != '':
			if not self._errors.has_key('pass_check'):
				self._errors['pass_check'] = ErrorList()
				self._errors["pass_check"].append(u'Passwords must match!')
	
		return cleaned_data

	def save(self):
		instance = super(AccountForm, self).save(self)

		cleaned_data = self.cleaned_data
		
		
		if 'newpass' in cleaned_data and cleaned_data['newpass']:
			instance.user.set_password(cleaned_data['newpass'])

		instance.name = cleaned_data['name']
		instance.description = cleaned_data['description']

		instance.user.save()

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
