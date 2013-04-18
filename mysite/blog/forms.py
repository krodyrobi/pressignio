from django import forms

import datetime		

class RegisterForm(forms.Form):
    	username = forms.CharField(max_length=30)
    	password = forms.CharField(widget=forms.PasswordInput)
	pass_check = forms.CharField(widget=forms.PasswordInput)
	
	reg_date_time = forms.DateTimeField(datetime.now())

	author_name = forms.CharField(max_length=100)
	author_description = form.TextField()

	email = forms.EmailField()
