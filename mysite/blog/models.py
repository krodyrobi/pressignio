from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils import timezone
from django import forms

class Author(models.Model):
	user = models.OneToOneField(User)
	name = models.CharField(max_length=100)
	slug = models.SlugField()
	description = models.TextField()
	confirmation_code = models.CharField(max_length = 35)
	recovery_code = models.CharField(max_length = 35)

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

def set_slug_author(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.name)

pre_save.connect(set_slug_author, sender=Author)

def set_slug_article(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.title)

pre_save.connect(set_slug_article, sender=Article)
