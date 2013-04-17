from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.template.defaultfilters import slugify
from django.utils import timezone

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

def set_slug(sender, instance, *args, **kwargs):
		instance.slug = slugify(instance.title)

pre_save.connect(set_slug, sender=Article)
