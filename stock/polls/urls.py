from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name="app-home"),
    path('logout/', views.logoutPage, name="logout"),
    path('all_stock/', views.all_stock, name="all-stock"),
    path('insert/', views.insert_elem, name="app-insert"),
    path('update/<str:pk>/', views.update_elem, name="app-update"),
    path('delete/<str:pk>/', views.delete, name="app-delete"),
    path('search/', views.search, name="app-search"),
    path('register/', views.register, name="app-register"),
    # path('login/', views.loginPage, name="app-login"),
    path('after_login/', views.home, name="app-after_login"),
]
