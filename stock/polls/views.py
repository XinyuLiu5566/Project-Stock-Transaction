from django.shortcuts import render
from django.http import HttpResponse

from .models import StockInfo
# Create your views here.


def showone(request, symbol_num):
    stock = StockInfo.objects.get(symbol=symbol_num)
    return HttpResponse(stock)
