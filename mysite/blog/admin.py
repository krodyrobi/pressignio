from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from blog.models import Article, UserProfile

class AuthorInline(admin.StackedInline):
	model = UserProfile
	fields = ("name", "description");

class UserAdmin(UserAdmin):
	inlines = (AuthorInline,)

class ArticleAdmin(admin.ModelAdmin):
	fieldsets = [
		('Header', {'fields': ['title', 'author']}),
		('Body', {'fields': ['text']})
	]
	list_display = ('title', 'author')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
