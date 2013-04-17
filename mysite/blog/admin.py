from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from blog.models import Author, Article

class AuthorInline(admin.StackedInline):
	model = Author

class UserAdmin(UserAdmin):
	inlines = (AuthorInline,)

class ArticleAdmin(admin.ModelAdmin):
	fieldsets = [
		('Header', {'fields': ['title', 'author', 'publication_date']}),
		('Body', {'fields': ['text']})
	]
	list_display = ('title', 'author', 'publication_date')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Article, ArticleAdmin)
