from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm, ValidationError
from django.forms.util import ErrorList
from django.db.models import Q


from blog.models import Article, Author

import string 
import datetime
import random


def sendValidationEmail(user, author):
	title = "Pressignio account confirmation:"
	content = "localhost:8000/blog/confirm/%s/%s/" % (author.confirmation_code, user.username)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)
	
def sendPasswordRecoveryConfirm(user):
	title = "Pressignio password recovery:"
	content = "localhost:8000/blog/passwordRecovery/%s/%s/" % (user.author.recovery_code, user.username)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)
	
def sendRetrievePasswordEmail(user):
	password = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(6))
	user.set_password(password)
	user.save()
	
	title = "Pressignio account password:"
	content = "Username:%s\nPassword:%s" % (user.username, password)
	send_mail(title, content, 'pressignio-bot@presslabs.com', [user.email], fail_silently=False)

class RegisterForm(forms.Form):
	username = forms.CharField(label="Username",max_length=30)
	password = forms.CharField(label="Password",widget=forms.PasswordInput,min_length=6)
	pass_check = forms.CharField(label="Re-type password",widget=forms.PasswordInput)

	author_name = forms.CharField(label="Author Name",max_length=100)
	author_description = forms.CharField(label="Description",widget=forms.Textarea)

	email = forms.EmailField(label="Email")

	def __init__(self, *args, **kwargs):
		super(RegisterForm, self).__init__(*args, **kwargs)


		for field in self.fields.values():
		    field.error_messages = {'required':'The field {fieldname} is required!'.format(fieldname=field.label)}


	def clean(self):
		cleaned_data = super(RegisterForm, self).clean()
      
		try:
			if 'username' in cleaned_data: 
				check = User.objects.get(username=cleaned_data['username'])
		except ObjectDoesNotExist:
			pass
		else:
			if not self._errors.has_key('username'):
				self._errors['username'] = ErrorList()
				self._errors['username'].append(u'Username already in use, choose another!')
				
		try:
			if 'email' in cleaned_data:
				check = User.objects.get(email=cleaned_data['email'])
		except ObjectDoesNotExist:
			pass
		else:
			if not self._errors.has_key('email'):
				self._errors['email'] = ErrorList()
				self._errors["email"].append(u'Email already in use!')
			
		try:
			if 'author_name' in cleaned_data:
				check = Author.objects.get(name__iexact=cleaned_data['author_name'])
		except ObjectDoesNotExist:
			pass
		else:
			if not self._errors.has_key('author_name'):
				self._errors['author_name'] = ErrorList()
				self._errors["author_name"].append(u'This name has already been taken, please choose another.')

		
		
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
		author = Author(user = user, name = cleaned_data['author_name'], description = cleaned_data['author_description'], confirmation_code = code)
		user.save()
		author.save()

		return user,author


class EmailResendForm(forms.Form):
	email = forms.EmailField()

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			check = Author.objects.get(user__email=email, user__is_active=False)
		except ObjectDoesNotExist:
			if not self._errors.has_key('email'):
				self._errors['email'] = ErrorList()
				self._errors['email'].append(u'Email not found or user already active!')
			
		return email
    	
	def resend(self, user, author):
		sendValidationEmail(user,author)
		
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
		user.author.recovery_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(35))
		user.author.save()
		sendPasswordRecoveryConfirm(user)


class AccountForm(ModelForm):
	class Meta:
		model = User
		exclude = ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_superuser', 'last_login', 'date_joined',
			'groups', 'user_permissions')

		fields = ['passw', 'pass_check', 'email', 'author_name', 'author_description']	

	passw = forms.CharField(label='Password',widget=forms.PasswordInput,min_length=6)
	pass_check = forms.CharField(label='Re-type password',widget=forms.PasswordInput)
	author_name = forms.CharField(max_length=100)
	author_description = forms.CharField(label='Description',widget=forms.Textarea)

	def clean(self):
		cleaned_data = super(AccountForm, self).clean()
		
		try:
			if 'author_name' in cleaned_data:
				check = Author.objects.get(name__iexact=cleaned_data['author_name'])
		except ObjectDoesNotExist:
			pass
		else:
			if not self._errors.has_key('author_name'):
				self._errors['author_name'] = ErrorList()
				self._errors["author_name"].append(u'This name has already been taken, please choose another.')

		if 'passw' in cleaned_data:

			password1 = cleaned_data['passw']
			password2 = cleaned_data['pass_check']

			if password1 != password2:
				if not self._errors.has_key('pass_check'):
					self._errors['pass_check'] = ErrorList()
					self._errors['pass_check'].append(u'Passwords must match!')

		return cleaned_data

	def save(self):
		instance = super(AccountForm, self).save(self)

		cleaned_data = self.cleaned_data

		instance.set_password(cleaned_data['passw'])

		instance.author.name = cleaned_data['author_name']
		instance.author.description = cleaned_data['author_description']

		instance.save()

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
