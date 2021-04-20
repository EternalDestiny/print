from django.shortcuts import render, redirect

from app.models import GcodeFile, RegisteredPrinter
from chat.models import Printer, Print

from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from app.form import PrinterForm
from django.forms.models import model_to_dict

from django.contrib.auth.decorators import login_required

import os


# Create your views here.t

def index(request):
    return render(request, 'index.html')


# @login_required
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
            Printer.objects.get_or_create(printer_id=printer_id)
        else:
            v = PrinterForm(prefix='vv')

        return render(request, 'register_printer.html', locals())

    if request.method == 'POST':
        v = PrinterForm(data=request.POST, prefix='vv')
        if v.is_valid():
            printer_id = request.POST['vv-printer_id']
            print(printer_id)
            result = RegisteredPrinter.objects.filter(printer_id=printer_id)
            if not result:
                v.save()
                Printer.objects.get_or_create(printer_id=printer_id)
            return redirect('/list/')
        else:
            error_msg = v.errors.as_json()
            return render(request, 'register_printer.html', locals())


def register_printer_plugin(request):
    if request.method == 'POST':
        data = request.POST
        printer_id = data.get('printer_id')
        owner = data.get('owner')
        address = data.get('address')
        if printer_id and owner and address:
            if RegisteredPrinter.objects.filter(printer_id=printer_id):
                return HttpResponse('already')
            else:
                RegisteredPrinter.objects.get_or_create(printer_id=printer_id, owner=owner, address=address)
                Printer.objects.get_or_create(printer_id=printer_id)
                return HttpResponse('success')
        else:
            return HttpResponse('fail')


def del_printer(request):
    if request.method == 'POST':
        RegisteredPrinter.objects.filter(printer_id=request.POST['printer_id']).delete()
        Printer.objects.filter(printer_id=request.POST['printer_id']).delete()
        return redirect('/list/')


def printerlist_api(request):
    printer_list = {}
    if request.method == 'GET':
        printer = Printer.objects.all()

        for p in printer:
            if p.ready:
                state = '在线，可供打印'
            # 找出打印的是什么
            elif p.printing:
                state = '打印中'
            elif p.cancelling:
                state = '正在取消'
            elif p.pausing:
                state = '暂停中'
            elif p.paused:
                state = '已暂停打印'
            elif not p.closedOrError:
                state = '打印机关闭或错误'
            else:
                state = '离线'
            printer_list[p.printer_id] = state
        return JsonResponse(printer_list, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        return JsonResponse(printer_list)


def print_api(request):
    if request.method == 'GET':
        print = Print.objects.all().first()
        # 当前仅实现一个
        # for print_job in print:
        if print:
            print_job = model_to_dict(print,
                                      fields=['estimatedPrintTime', 'averagePrintTime',
                                              'completion', 'printTime', 'printTimeLeft', ])
        else:
            print_job = {'msg': '当前无任务'}
    return JsonResponse(print_job, json_dumps_params={'ensure_ascii': False})


def delgcodedata(request):
    if request.method == 'POST':
        if GcodeFile.objects.filter(gcode_id=request.POST['gcode_id']):
            gcode_file_sel = GcodeFile.objects.get(gcode_id=request.POST['gcode_id'])
            if gcode_file_sel.gcode_printing:
                return HttpResponse('文件正在打印，请等待打印完成')
            gcode_path = model_to_dict(gcode_file_sel)['gcode_safepath']
            gcode_file_sel.delete()
            try:
                os.remove(gcode_path)
            except Exception:
                return redirect('/list/')
            return redirect('/list/')
        else:
            return redirect('/list/')
    if request.method == 'GET':
        gcode_file_sel = GcodeFile.objects.all().first()
        if gcode_file_sel:
            if gcode_file_sel.gcode_printing:
                return HttpResponse('文件正在打印，请等待打印完成')
            gcode_path = model_to_dict(gcode_file_sel)['gcode_safepath']
            try:
                os.remove(gcode_path)
            except Exception:
                return redirect('/list/')
            gcode_file_sel.delete()
            return redirect('/list/')
        else:
            return redirect('/list/')


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

    if GcodeFile.objects.all().first():
        return HttpResponse('已有文件上传，请先打印')
    if request.method == 'POST':
        gcode_file_re = request.FILES.get("gcode_file", None)
        gcode_path = os.path.join(gcode_folder, gcode_file_re.name)
        if not gcode_file_re:
            return HttpResponse("no files for upload!")
        with open(gcode_path, 'wb+') as f:
            for chunk in gcode_file_re.chunks():
                f.write(chunk)

        develop = True
        if develop:
            server = 'http://127.0.0.1:8000'
        else:
            server = 'http://49.234.134.71'

        GcodeFile.objects.get_or_create(
            gcode_name=gcode_file_re.name,
            gcode_url=server + '/download_gcode_file/' + gcode_file_re.name,
            gcode_safepath=gcode_path,
            gcode_printed='False',
            gcode_selected='False',
        )
        # return HttpResponse("uploaded over, print started!")
        return redirect('/list/')
    else:
        return redirect('/list/')


def print_gcode(request):
    if request.method == 'POST':
        gcode_id = request.POST['gcode_id']
        GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='True')
        return redirect('/list/')
    if request.method == 'GET':
        gcode_file_sel = GcodeFile.objects.all().first()
        if gcode_file_sel:
            gcode_id = model_to_dict(gcode_file_sel)['gcode_id']
            GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='True')
            return redirect('/list/')
        else:
            return redirect('/list/')


# develop
def del_alldata(request):
    Printer.objects.all().delete()
    RegisteredPrinter.objects.all().delete()
    GcodeFile.objects.all().delete()
    Print.objects.all().delete()
    return HttpResponse('数据库文件已删除')


def get_all_model(request):
    if request.method == 'GET':
        printer_state = Printer.objects.all()
        gcodefile = GcodeFile.objects.all()
        print_job = Print.objects.all()
        return render(request, 'develop.html', locals())


def delprinterdata(request):
    Printer.objects.all().delete()
    return redirect('/list/')

def list(request):
    if request.method == 'GET':
        printer = RegisteredPrinter.objects.all()
        gcode = GcodeFile.objects.all()
        return render(request, 'list_websocket.html', context={'printer': printer, 'gcode': gcode})