from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django import forms

class Author(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField(max_length=100)
	description = models.TextField()

	def __unicode__(self):
		return self.name

class Article(models.Model):
	title = models.CharField(max_length=200)
	slug = models.SlugField()
	text = models.TextField()
	author = models.ForeignKey(Author)
	publication_date = models.DateTimeField()
	
	def __unicode__(self):
		return self.title + ' - ' + self.author.name

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)

		super(Article, self).save(*args, **kwargs)
		

class RegisterForm(forms.Form):
    	username = forms.CharField(max_length=30)
    	password = forms.CharField(widget=forms.PasswordInput)

	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)

	email = forms.EmailField()
