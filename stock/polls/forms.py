from .models import StockInfo
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class StockCreateForm(forms.ModelForm):
   class Meta:
     model = StockInfo
     fields = ['ts_code', 'symbol', 'enname', 'list_date']



class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']