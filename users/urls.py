"""print URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path, re_path
from .views import *

urlpatterns = [
    # 默认进入登录界面
    path('', loginView, name='login'),
    path('login', loginView, name='login'),
    # 注册
    path('register', registerView, name='register'),
    # 修改密码
    path('setps', setpsView, name='setps'),
    # 登出
    path('logout', logoutView, name='logout'),
]
