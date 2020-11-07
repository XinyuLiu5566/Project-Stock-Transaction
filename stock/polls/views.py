from django.shortcuts import render
from django.http import HttpResponse
from .forms import *
from .models import *

def home(request):
    title = "Stock mainpage"
    context = {
        "title" : title
    }
    return render(request, 'polls/home.html', context)


    
def all_stock(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    context = {
        "title" : title,
        "queryset" : queryset,
    }
    return render(request, 'polls/all_stock.html', context)


def insert_elem(request):
    title = "insert"
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        # return redirect('polls/all_stock.html')
    context = {
        "form" : form,
        "title": title,
    }
    return render(request, 'polls/insert.html', context)
# Create your views here.