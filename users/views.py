from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate


# 用户注册
def registerView(request):
    # 设置模版上下文
    title = '注册'
    pageTitle = '用户注册'
    if request.method == 'POST':
        u = request.POST.get('username', '')
        p = request.POST.get('password', '')
        if User.objects.filter(username=u):
            tips = '用户已存在'
        else:
            d = dict(username=u, password=p, is_staff=0, is_superuser=0)
            user = User.objects.create_user(**d)
            user.save()
            tips = '注册成功，请登录'
    return render(request, 'user.html', locals())


# 用户登录
def loginView(request):
    # 设置模版上下文
    title = '登录'
    pageTitle = '用户登录'
    if request.method == 'POST':
        p = request.POST.get('password', '')
        u = request.POST.get('username', '')
        if User.objects.filter(username=u):
            user = authenticate(username=u, password=p)
            if user:
                if user.is_active:
                    login(request, user)
                return HttpResponse('登录成功')
            else:
                tips = '账号密码错误，请重新输入'
        else:
            tips = '用户不存在，请注册'
    return render(request, 'user.html', locals())


# 修改密码
def setpsView(request):
    # 设置模版上下文
    title = '修改密码'
    pageTitle = '修改密码'
    password2 = True
    if request.method == 'POST':
        u = request.POST.get('username', '')
        p = request.POST.get('password', '')
        p2 = request.POST.get('password2', '')
        if User.objects.filter(username=u):
            user = authenticate(username=u, password=p)
            # 判断用户的账号密码是否正确
            if user:
                user.set_password(p2)
                user.save()
                tips = '密码修改成功'
            else:
                tips = '原始密码不正确'
        else:
            tips = '用户不存在'
    return render(request, 'user.html', locals())


# 使用make_password实现密码修改
from django.contrib.auth.hashers import make_password


def setpsView2(request):
    # 设置模版上下文
    title = '修改密码'
    pageTitle = '修改密码'
    password2 = True
    if request.method == 'POST':
        u = request.POST.get('username', '')
        p = request.POST.get('password', '')
        p2 = request.POST.get('password2', '')
        # 判断用户是否存在
        user = User.objects.filter(username=u)
        if User.objects.filter(username=u):
            user = authenticate(username=u, password=p)
            # 判断用户的账号密码是否正确
            if user:
                # 密码加密处理并保存到数据库
                dj_ps = make_password(p2, None, 'pbkdf2_sha256')
                user.password = dj_ps
                user.save()
            else:
                print('原始密码不正确')
    return render(request, 'user.html', locals())


# 用户注销，退出登录
def logoutView(request):
    logout(request)
    return HttpResponse('注销成功')
