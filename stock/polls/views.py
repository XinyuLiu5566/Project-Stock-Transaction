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
            usernode = Person(name=user)
            db.set_connection('bolt://neo4j:000000@localhost:7687')
            usernode.save()
            messages.success(request, 'Account was created for ' + user)

            return redirect('../../polls/')
    context = {
        "title": title,
        "form": form
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
            "title": title,
            "queryset": queryset,
        }
        return render(request, 'polls/all_stock.html', context)
    else:
        username = request.user.username
        user = Person.nodes.get(name=username)
        query = "match (n:Person) -[r:own]-> (t:Transaction) where n.name = '" + \
            username + "' return t"
        results, meta = db.cypher_query(query)
        queryset = [Transaction.inflate(row[0]) for row in results]
        console.log(queryset)
        title = "Stock mainpage"
        context = {
            "title": title,
            "queryset": queryset
        }
        return render(request, 'polls/home_after_login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('../polls')


def home(request):
    db.set_connection('bolt://neo4j:000000@localhost:7687')
    if request.user.username == 'admin':
        title = "all stock info"
        queryset = StockInfo.objects.all()
        # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
        context = {
            "title": title,
            "queryset": queryset,
        }
        return render(request, 'polls/all_stock.html', context)
    else:
        username = request.user.username
        user = Person.nodes.get(name=username)
        query = "match (n:Person) -[r:own]-> (t:Transaction) where n.name = '" + \
            username + "' return t"
        results, meta = db.cypher_query(query)
        queryset = [Transaction.inflate(row[0]) for row in results]
        company = []
        for i in range(len(queryset)):
            name = StockInfo.objects.get(ts_code=queryset[i].ts_code)
            company.append(name)

        date = request.POST.get('search_recommmand')
        results = []
        if date != '':
            # temp = predict(date)
            # for i in range(len(temp)):
            #     name = StockInfo.objects.get(ts_code=i)
            #     results.append(name)
            cursor = connection.cursor()
            cursor.execute("SELECT ts_code,enname FROM adf1_result WHERE trade_date = '"+str(date)+"'")
            results = cursor.fetchall()
        title = "Stock mainpage"
        context = {
            "title": title,
            # "queryset" : queryset,
            "company": company,
            "results": results,
        }
        return render(request, 'polls/home.html', context)


def daily_info(request):
    title = "stock daily info"
    cursor = connection.cursor()
    cursor.execute("SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info LIMIT 1000")
    results = cursor.fetchall()
    # queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title": title,
        "queryset": results,
    }
    return render(request, 'polls/daily_info.html', context)


def all_stock(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title": title,
        "queryset": queryset,
    }
    return render(request, 'polls/all_stock.html', context)


def all_stock_not_admin(request):
    title = "all stock info"
    queryset = StockInfo.objects.all()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title": title,
        "queryset": queryset,
    }
    return render(request, 'polls/all_stock_not_admin.html', context)


def insert_elem(request):
    title = "insert"
    form = StockCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('../../../polls/all_stock')
    context = {
        "form": form,
        "title": title,
    }
    return render(request, 'polls/insert.html', context)


def insert_neo(request):
    db.set_connection('bolt://neo4j:000000@localhost:7687')
    title = "insert"
    form = StockForm(request.POST or None)
    flag = 1
    if form.is_valid():
        code = form.data['input_code']
        print(type(code))
        try:
            user = StockInfo.objects.get(ts_code=code)
        except ObjectDoesNotExist:
            flag = 0
        if flag == 1:
            ts = Transaction.nodes.get_or_none(ts_code=code)
            if ts is None:
                ts = Transaction(ts_code=code).save()

            usernode = Person.nodes.get(name=request.user.username)
            usernode.stock.connect(ts)
            return redirect('../after_login')
    context = {
        "form": form,
        "title": title,
    }
    return render(request, 'polls/insertneo.html', context)


def more_info(request, pk):
    db.set_connection('bolt://neo4j:000000@localhost:7687')
    stock = StockInfo.objects.get(ts_code=pk)
    cursor = connection.cursor()
    cursor.execute("SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info WHERE ts_code = '" + str(pk) + "'")
    results = cursor.fetchall()
    username = request.user.username
    user = Person.nodes.get(name=username)
    # 0 return recommendation_adv, 1 return unpopular text and recommendation_default, 2 return followmore text
    recstate = 0
    text_unpopular = "This is a unpopular stock, here are some recommending stock based on stock you own: "
    text_ownmore = "Own more stock to get personalized recommendation!"
    query_adv = "MATCH (cu:Person{name:'" + username + "'})-[r:own]->(s:Transaction)<-[rr:own]-(sou:Person) WITH sou, cu MATCH (a:Transaction{ts_code:'" + pk + \
        "'}) <-[r:own]-(b:Person) WITH DISTINCT b, a, sou, cu MATCH (b)-[r:own]->(rs:Transaction) WHERE a <> rs AND (NOT (cu)--(rs)) WITH DISTINCT rs, sou MATCH (rs)<-[r:own]-(uo:Person) WITH rs, count(DISTINCT uo) as de_weight, collect(distinct uo) as owner, collect(distinct sou) as close_user WITH rs, de_weight, owner, close_user, [n in owner WHERE n in close_user] as high_weight_user, 2 * size([n in owner WHERE n in close_user]) as bonus RETURN rs.ts_code, de_weight + bonus as final_weight ORDER BY final_weight DESC LIMIT 5"
    neoresults_adv, meta_adv = db.cypher_query(query_adv)
    recommendation_adv = [row[0] for row in neoresults_adv]
    if (len(recommendation_adv) == 0):
        recstate = 1
    query_default = "MATCH (cu:Person{name:'" + username + \
        "'})-[r:own]-(s:Transaction)<-[rr:own]-(sou:Person) WITH sou, cu, COUNT(s) as weight MATCH (sou)-[r:own]->(a:Transaction) WHERE NOT (cu)--(a) RETURN weight, a.ts_code ORDER BY weight DESC"
    neoresults_default, meta_default = db.cypher_query(query_default)
    recommendation_default = []
    for x in neoresults_default:
        if (x[1] not in recommendation_default):
            recommendation_default.insert(len(recommendation_default), x[1])
        if (len(recommendation_default) >= 5):
            break
    if (len(recommendation_default) == 0):
        recstate = 2

    if (recstate == 0):
        queryset = recommendation_adv
        warning_text = "This is the recommandation stock based on" + pk + ":"
    elif (recstate == 1):
        queryset = recommendation_default
        warning_text = text_unpopular
    elif (recstate == 2):
        queryset = []
        warning_text = text_ownmore

    company = []
    for i in range(len(queryset)):
        st = StockInfo.objects.get(ts_code=queryset[i])
        company.append(st.enname)
    rank = range(1, len(queryset))
    queryset = list(zip(rank, queryset, company))

    context = {
        "daily": results,
        "stock": stock,
        "queryset": queryset,
        "warning_text": warning_text}
    # stock = StockInfo.objects.raw('''SELECT * FROM stock_info WHERE ts_code = %s''', pk)

    return render(request, 'polls/moreinfo.html', context)


def update_elem(request, pk):
    stock = StockInfo.objects.get(ts_code=pk)
    # stock = StockInfo.objects.raw('''SELECT * FROM stock_info WHERE ts_code = %s''', pk)
    form = StockCreateForm(request.POST or None, instance=stock)
    if form.is_valid():
        form.save()
        return redirect('../../../polls/all_stock')
    context = {
        "form": form,
    }
    return render(request, 'polls/insert.html', context)


def delete(request, pk):
    stock = StockInfo.objects.get(ts_code=pk)
    if request.method == "POST":
        stock.delete()
        return redirect('../../../polls/all_stock')
    context = {
        "item": stock,
    }
    return render(request, 'polls/delete.html', context)


def delete_own(request, pk):
    db.set_connection('bolt://neo4j:000000@localhost:7687')
    if request.method == "POST":
        query = "MATCH (n:Transaction{ts_code:'"+pk+"'}) DETACH DELETE n"
        results, meta = db.cypher_query(query)
        return redirect('../../after_login')

    return render(request, 'polls/delete_own.html')

def search(request):
    code = request.POST['search']
    title = "search result"
    if code != '':
        queryset = StockInfo.objects.get(ts_code=code)
        # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
        context = {
            "title": title,
            "queryset": queryset,
        }
        return render(request, 'polls/search.html', context)
    else:
        title = "all stock info"
        queryset = StockInfo.objects.all()
        # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
        context = {
            "title": title,
            "queryset": queryset,
        }
        return render(request, 'polls/all_stock.html', context)
# Create your views here.


def search_daily(request):
    code = request.POST.get('search_ts', False)
    date = request.POST.get('search_date', False)
    value = request.POST.get('order_by')
    title = "search result"
    cursor = connection.cursor()
    if code != '':
        query = "SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info WHERE ts_code = '" + \
            str(code) + "'"

    if date != '':
        query = "SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info WHERE trade_date = '" + \
            str(date) + "'"

    if code != '' and date != '':
        query = "SELECT ts_code, enname, trade_date, open_price, high, low, close_price, percent_change,volumn FROM daily_info NATURAL JOIN stock_info" + \
            " WHERE ts_code = '" + str(code) + "'" + "and trade_date = '" + str(date) + "'"

    if value == "Price low to high":
        query = query + "ORDER BY close_price"
    if value == "Price high to low":
        query = query + "ORDER BY close_price DESC"
    cursor.execute(query)
    results = cursor.fetchall()
    # queryset = StockInfo.objects.raw('''SELECT * FROM stock_info''')
    context = {
        "title": title,
        "queryset": results
    }
    return render(request, 'polls/search_daily.html', context)
