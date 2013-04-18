from django import forms


class RegisterForm(forms.Form):
    	username = forms.CharField(max_length=30)
    	password = forms.CharField(widget=forms.PasswordInput)
	pass_check = forms.CharField(widget=forms.PasswordInput)

	author_name = forms.CharField(max_length=100)
	author_description = forms.CharField(widget=forms.Textarea)

	email = forms.EmailField()

	def clean(self):
		cleaned_data = self.cleaned_data
		
		password1 = cleaned_data.get("password")
		password2 = cleaned_data.get("pass_check")


		if password1 != password2:
			raise forms.ValidationError("Passwords must be identical.")

		return cleaned_data
