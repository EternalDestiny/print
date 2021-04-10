from django.shortcuts import render, redirect

from app.models import Cal, Printer, GcodeFile, RegisteredPrinter
from django.http import FileResponse, JsonResponse, HttpResponse, Http404

from app.form import PrinterForm

# Create your views here.

# def index(request):
# return render(request,'index.html')

import os


def calpage(request):
    return render(request, 'cal.html')


def calculate(request):
    if request.POST:
        value_a = request.POST['valueA']
        value_b = request.POST['valueB']
        result = int(value_a) + int(value_b)
        Cal.objects.create(value_a=value_a, value_b=value_b, result=result)
        return render(request, 'result.html', context={'data': result})
    else:
        return HttpResponse("please visit us with POST")


def printerlist(request):
    if request.method == 'GET':
        printer = RegisteredPrinter.objects.all()
        gcode = GcodeFile.objects.all()
        return render(request, 'list.html', context={'printer': printer, 'gcode': gcode})


def register_printer(request):
    if request.method == 'GET':
        printer_id = request.GET.get('printer_id', '')
        if printer_id:
            i = RegisteredPrinter.objects.filter(printer_id=printer_id).first()
            v = PrinterForm(instance=i, prefix='vv')
        else:
            print("hah")
            v = PrinterForm(prefix='vv')

        return render(request, 'register_printer.html', locals())

    if request.method == 'POST':
        v = PrinterForm(data=request.POST, prefix='vv')
        if v.is_valid():
            printer_id = v['printer_id']
            owner = v['owner']
            address = v['address']
            result = RegisteredPrinter.objects.filter(printer_id=printer_id)
            if not result:
                v.save()
            return redirect('/list/')
        else:
            error_msg = v.errors.as_json()
            return render(request, 'register_printer.html', locals())

def del_printer(request):
    if request.method == 'PSOT':
        printer_sel = RegisteredPrinter.objects.filter(printer_id=request.POST['printer_id'])
        printer_sel.delete()
        return redirect('/list/')

def printerlist_api(request):
    printer_list = {}
    if request.method == 'GET':
        printer_on = Printer.objects.filter(is_ready='True').values('printer_id')
        printer_off = Printer.objects.filter(is_ready='False').values('printer_id')
        for pon in printer_on:
            printer_list[pon['printer_id']] = 'Online'
        for poff in printer_off:
            printer_list[poff['printer_id']] = 'Offline'
        return JsonResponse(printer_list)
    if request.method == 'POST':
        pass


def delprinterdata(request):
    Printer.objects.all().delete()
    return redirect('/list/')


def delgcodedata(request):
    if request.method == 'POST':
        gcode_file_sel = GcodeFile.objects.filter(gcode_id=request.POST['gcode_id'])
        gcode_path = GcodeFile.objects.values('gcode_safepath').get(gcode_id=request.POST['gcode_id'])[
            'gcode_safepath']
        print(gcode_path)
        try:
            os.remove(gcode_path)
        except Exception:
            pass
        gcode_file_sel.delete()
    return redirect('/list/')


def getresponse(request):
    return render(request, 'getresponse.html')


#
def downloadindex(request):
    return render(request, 'downloadindex.html')


def download1(request):
    file_path = "/gcodefiles\\Gnomon_Northen.gcode"
    try:
        # r=FileResponse(open(file_path, 'rb'))
        # r['content_type']='application/ocet-stream'
        # r['content_Disposition'] = 'attachment;filename=Gnomon_Northen.gcode'
        f = open(file_path, 'rb')
        r = FileResponse(f, as_attachment=True, filename='Gnomon_Northen.gcode')
        return r
    except Exception:
        raise Http404('download error')


def download_gcode_file(request, filename):
    if request.method == 'GET':
        gcode_folder = os.path.join(os.getcwd(), "gcodefiles")
        file_path = os.path.join(gcode_folder, filename)

        try:
            f = open(file_path, 'rb')
            r = FileResponse(f, as_attachment=True, filename=filename)
            return r
        except Exception:
            raise Http404('download error')


def upload_gcode_file(request):
    gcode_folder = os.path.join(os.getcwd(), "gcodefiles")
    if not os.path.exists(gcode_folder):
        os.makedirs("gcodefiles")

    if request.method == 'POST':
        gcode_file_re = request.FILES.get("gcode_file", None)
        gcode_path = os.path.join(gcode_folder, gcode_file_re.name)
        if not gcode_file_re:
            return HttpResponse("no files for upload!")
        with open(gcode_path, 'wb+') as f:
            for chunk in gcode_file_re.chunks():
                f.write(chunk)

        GcodeFile.objects.get_or_create(
            gcode_name=gcode_file_re.name,
            gcode_url='127.0.0.1:8000/download_gcode_file/' + gcode_file_re.name,
            gcode_safepath=gcode_path,
            gcode_printed='False',
            gcode_selected='False',
        )
        # return HttpResponse("uploaded over, print started!")
        return redirect('/list/')
    else:
        return render(request, 'upload_gcode.html')


def print_gcode(request):
    if request.method == 'POST':
        gcode_id = request.POST['gcode_id']
        GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='True')
    return redirect('/list/')


def test(request):
    if request.method == 'POST':
        printer_state = request.POST
        print('POST from', printer_state['printer_id'])

        # 将打印机状态写入数据库
        Printer.objects.get_or_create(
            printer_id=printer_state['printer_id'],
        )

        Printer.objects.filter(printer_id=printer_state['printer_id']).update(
            is_operational=printer_state['is_operational'],
            is_printing=printer_state['is_printing'],
            is_cancelling=printer_state['is_cancelling'],
            is_closed_or_error=printer_state['is_closed_or_error'],
            is_paused=printer_state['is_paused'],
            is_pausing=printer_state['is_pausing'],
            is_ready=printer_state['is_ready'],
        )

        # Printer.objects.all().delete()

        try:
            # 查询是否有需要打印的gcode
            gcode_set = GcodeFile.objects.all()
            gcode_id = gcode_set.values('gcode_id').get(gcode_selected='True')['gcode_id']
            print("有文件需要打印")
            gcode_path = gcode_set.values('gcode_safepath').get(gcode_selected='True')['gcode_safepath']
            # print(gcode_path)
            gcode_name = gcode_set.values('gcode_name').get(gcode_selected='True')['gcode_name']
            # print(printer_state['is_operational'])

            if printer_state['is_ready'] == 'True':
                try:
                    f = open(gcode_path, 'rb')
                    r = FileResponse(f, as_attachment=True, filename=gcode_name)
                    GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printed='True')
                    GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='False')
                    GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printer_id=printer_state['printer_id'])
                    # 应该要remove
                    return r
                except Exception:
                    return Http404('error')
        except Exception:
            return HttpResponse('recieved')
    if request.GET:
        pass

# def register_print(request):
#     if request.method == 'GET':
#         return render(request, 'register.html')
#
#     if request.method == 'POST':
#         printer_id = request.POST["请输入printer_id"]
#         owner = request.POST["请输入owner"]
#         address = request.POST["请输入adress"]
#
#         if not printer_id:
#             return HttpResponse('printer_id不能为空')
#         if not owner:
#             return HttpResponse('密码不能为空')
#         if not address:
#             return HttpResponse('确认密码不能为空')
#         if username and password and repeat_password:
#             if password == repeat_password:
#                 # filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回由符合条件元素组成的新列表
#                 user_project = models.User.objects.filter(username=username).first()
#                 if user_project:
#                     return HttpResponse('用户名已存在')
#                 else:
#                     models.User.objects.create(username=username, password=password).save()
#                     return redirect('/login/')
#             else:
#                 return HttpResponse('两次输入的密码不一致')
