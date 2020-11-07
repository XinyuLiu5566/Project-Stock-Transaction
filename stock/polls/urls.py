from django.urls import path
from . import views
from .forms import *
urlpatterns = [
    path('', views.home, name="app-home"),
    path('all_stock/', views.all_stock, name="all-stock"),
    path('insert/', views.insert_elem, name="app-insert"),
]
