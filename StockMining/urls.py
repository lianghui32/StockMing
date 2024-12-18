"""StockMining URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stock_all.views import user, prediction, market, home, account,tools

urlpatterns = [
    path("", home.home_all, name='index'),
    path('search_stocks/', tools.search_stocks, name='search_stocks'),

    path('image/code/', account.image_code, name='image_code'),

    path("admin/", admin.site.urls, name='admin'),
    path("home/", home.home_all, name='home'),

    path("market/", market.market_tb),
    path("market/Today_data/", market.Today_data, name='Today_data'),
    path("market/get_stock_name/", market.get_stock_name, name='get_stock_name'),

    path("prediction/", prediction.show_pre),
    path("prediction/lstm/", prediction.lstm_pre, name="lstm_pre"),
    path("prediction/rf/", prediction.rf_pre, name="rf_pre"),

    path('user_view/', user.user_view, name='user_view'),
    path('user_edit/', user.user_edit, name='user_edit'),
    path('user_save/', user.user_save, name='user_save'),

    # 登录
    path('register/', account.register_view, name='register'),
    path('login/', account.login_view, name='login'),
    path('logout/', account.logout_view, name='logout'),
    path('change_password/', user.change_password, name='change_password'),
]
