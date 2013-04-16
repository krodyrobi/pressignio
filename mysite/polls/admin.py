from polls.models import *
from django.contrib import admin

class ChoiceInline(admin.TabularInline):
	model = Choice
	extra = 3

class PollAdmin(admin.ModelAdmin):
	list_display = ('question', 'pub_date', 'was_published_recently')
	list_filter = ['pub_date']
	date_hierarchy = 'pub_date'
	fieldsets = [
		(None,               {'fields': ['question']}),
		('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
	]
	inlines = [ChoiceInline]
	search_fields = ['question']

admin.site.register(Poll, PollAdmin)
