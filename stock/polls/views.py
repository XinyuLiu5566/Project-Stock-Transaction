from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm


from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def register(request):
    title = "register"
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)

            return redirect('../../polls/login')
    context = {
        "title" : title,
        "form" : form
    }
    return render(request, 'polls/register.html', context)


def loginPage(request):
    title = "login"
    if request.method == 'POST':
        username = request.POST.get('username')
        password =request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('../polls/after_login')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'polls/login.html', context)

def home_afterlogin(request):
    title = "Stock mainpage"
    context = {
        "title" : title
    }
    return render(request, 'polls/home_after_login.html', context)


def logoutPage(request):
	logout(request)
	return redirect('login')


def home(request):
    title = "Stock mainpage"
    context = {
        "title" : title
    }
    return render(request, 'polls/home.html', context)


    
def all_stock(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
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


def update_elem(request, pk):
    stock = StockInfo.objects.get(ts_code = pk)
    # stock = StockInfo.objects.raw('''SELECT * FROM stock_info WHERE ts_code = %s''', pk)
    form = StockCreateForm(request.POST or None, instance = stock) 
    if form.is_valid():
        form.save()
    context = {
        "form" : form,
    }
    return render(request, 'polls/insert.html', context)

def delete(request, pk):
    stock = StockInfo.objects.get(ts_code = pk)
    if request.method == "POST":
        stock.delete()
        return redirect('../../../polls/all_stock')
    context = {
        "item" : stock,
    }
    return render(request, 'polls/delete.html', context)

def search(request):
    code = request.POST['search']
    title = "search result"
    queryset = StockInfo.objects.get(ts_code = code)
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title" : title,
        "queryset" : queryset,
    }
    return render(request, 'polls/search.html', context)
# Create your views here.
