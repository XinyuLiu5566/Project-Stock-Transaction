from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from neomodel import config
from neomodel import db
from django.db import connection

def register(request):
    title = "register"
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            usernode = Person(name = user)
            config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
            usernode.save()
            messages.success(request, 'Account was created for ' + user)

            return redirect('../../polls/')
    context = {
        "title" : title,
        "form" : form
    }
    return render(request, 'polls/register.html', context)


def loginPage(request):
    title = "login"
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if username == 'admin':
                return redirect('../polls/all_stock')
            else:
                return redirect('../polls/after_login')
        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'polls/login.html', context)

def home_afterlogin(request):
    console.log('123')
    if request.user.username == 'admin':
        title = "all stock info"
        queryset = StockInfo.objects.all()
        # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
        context = {
            "title" : title,
            "queryset" : queryset,
        }
        return render(request, 'polls/all_stock.html', context)
    else:
        username = request.user.username
        user = Person.nodes.get(name=username)
        query = "match (n:Person) -[r:own]-> (t:Transaction) where n.name = '"+ username +"' return t"
        results, meta = db.cypher_query(query)
        queryset = [Transaction.inflate(row[0]) for row in results]
        console.log(queryset)
        title = "Stock mainpage"
        context = {
            "title" : title,
            "queryset" : queryset
        }
        return render(request, 'polls/home_after_login.html', context)


def logoutPage(request):
	logout(request)
	return redirect('../polls')


def home(request):
    config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
    if request.user.username == 'admin':
        title = "all stock info"
        queryset = StockInfo.objects.all()
        # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
        context = {
            "title" : title,
            "queryset" : queryset,
        }
        return render(request, 'polls/all_stock.html', context)
    else:
        username = request.user.username
        user = Person.nodes.get(name=username)
        query = "match (n:Person) -[r:own]-> (t:Transaction) where n.name = '"+ username +"' return t"
        results, meta = db.cypher_query(query)
        queryset = [Transaction.inflate(row[0]) for row in results]
        print(queryset)
        title = "Stock mainpage"
        context = {
            "title" : title,
            "queryset" : queryset
        }
        return render(request, 'polls/home.html', context)

def daily_info(request):
    title = "stock daily info"
    cursor = connection.cursor()
    cursor.execute("SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info")
    results = cursor.fetchall()
    # queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title" : title,
        "queryset" : results,
    }
    return render(request, 'polls/daily_info.html', context)
    
def all_stock(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title" : title,
        "queryset" : queryset,
    }
    return render(request, 'polls/all_stock.html', context)

def all_stock_not_admin(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title" : title,
        "queryset" : queryset,
    }
    return render(request, 'polls/all_stock_not_admin.html', context)


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

def insert_neo(request):
    config.DATABASE_URL = os.environ["NEO4J_BOLT_URL"]
    title = "insert"
    form = StockForm(request.POST or None)
    flag = 1
    if form.is_valid():
        code = form.data['input_code']
        print(type(code))
        try:
            user = StockInfo.objects.get(ts_code = code)
        except ObjectDoesNotExist:
            flag = 0
        if flag == 1:
            ts = Transaction.nodes.get_or_none(ts_code = code)
            if ts is None:
                ts = Transaction(ts_code = code).save()
            
            usernode = Person.nodes.get(name=request.user.username)
            usernode.stock.connect(ts)
            return redirect('../after_login')
    context = {
        "form" : form,
        "title": title,
    }
    return render(request, 'polls/insertneo.html', context)



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
