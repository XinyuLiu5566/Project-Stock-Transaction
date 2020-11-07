from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="app-home"),
    path('all_stock/', views.all_stock, name="all-stock"),
    path('insert/', views.insert_elem, name="app-insert"),
    path('update/<str:pk>/', views.update_elem, name="app-update"),
    path('delete/<str:pk>/', views.delete, name="app-delete"),

]
