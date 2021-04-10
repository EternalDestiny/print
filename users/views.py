from django.shortcuts import render, HttpResponse, redirect
from users import models

# Create your views here.
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        username = request.POST.get('请输入用户名')
        password = request.POST.get('请输入密码')
        user_obj = models.User.objects.filter(username=username, password=password).first()
        if user_obj:
            return redirect('/calpage/')
        else:
            return HttpResponse('用户名或密码错误')

def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        username = request.POST["请输入用户名"]
        password = request.POST["请输入密码"]
        repeat_password = request.POST["请输入确认密码"]
        if not username:
            return HttpResponse('用户名不能为空')
        if not password:
            return HttpResponse('密码不能为空')
        if not repeat_password:
            return HttpResponse('确认密码不能为空')
        if username and password and repeat_password:
            if password == repeat_password:
                # filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回由符合条件元素组成的新列表
                user_project = models.User.objects.filter(username=username).first()
                if user_project:
                    return HttpResponse('用户名已存在')
                else:
                    models.User.objects.create(username=username, password=password).save()
                    return redirect('/login/')
            else:
                return HttpResponse('两次输入的密码不一致')
