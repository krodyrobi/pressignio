from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify

class UserProfile(models.Model):
	user = models.ForeignKey(User, unique = True)
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
	author = models.ForeignKey(UserProfile)
	publication_date = models.DateTimeField(auto_now_add=True)

	
	def __unicode__(self):
		return self.title + ' - ' + self.author.name

def set_slug_author(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.name)

pre_save.connect(set_slug_author, sender=UserProfile)

def set_slug_article(sender, instance, *args, **kwargs):
	instance.slug = slugify(instance.title)

pre_save.connect(set_slug_article, sender=Article)
