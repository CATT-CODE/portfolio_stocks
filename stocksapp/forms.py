from django import forms
from .models import Account

class AccountForm(forms.ModelForm):
	class Meta:
		model = Account
		fields = ['username', 'password', 'firstName', 'lastName']
		widgets = {
      'password': forms.PasswordInput(),
    }		
	
	def __init__(self, *args, **kwargs):
		super(AccountForm, self).__init__(*args, **kwargs)
		for visible in self.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

