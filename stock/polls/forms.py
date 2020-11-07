from .models import StockInfo
from django import forms

class StockCreateForm(forms.ModelForm):
   class Meta:
     model = StockInfo
     fields = ['ts_code', 'symbol', 'enname', 'list_date']