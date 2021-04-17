from django.shortcuts import render, redirect

from app.models import Printer, GcodeFile, RegisteredPrinter
from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from app.form import PrinterForm
from django.forms.models import model_to_dict

from django.contrib.auth.decorators import login_required

# Create your views here.t

def index(request):
    return render(request, 'index.html')


import os


@login_required
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
            if p.is_ready == 'True':
                state = '在线，可供打印'
            elif p.is_printing == 'True':
                state = '打印中'
            elif p.is_cancelling == 'True':
                state = '正在取消'
            elif p.is_pausing == 'True':
                state = '暂停中'
            elif p.is_paused == 'True':
                state = '已暂停打印'
            elif p.is_closed_or_error == 'True':
                state = '打印机关闭或错误'
            else:
                state = '离线'
            printer_list[p.printer_id] = state
        return JsonResponse(printer_list, json_dumps_params={'ensure_ascii': False})
        # return JsonResponse({'chen':'chen'})

    if request.method == 'POST':
        return JsonResponse(printer_list)





def delprinterdata(request):
    Printer.objects.all().delete()
    return redirect('/list/')


def delgcodedata(request):
    if request.method == 'POST':
        if GcodeFile.objects.filter(gcode_id=request.POST['gcode_id']):
            gcode_file_sel = GcodeFile.objects.get(gcode_id=request.POST['gcode_id'])
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

        server = 'http://127.0.0.1:8000'
        # server = 'http://49.234.134.71'
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


# def test(request):
#     if request.method == 'POST':
#         printer_data = request.POST
#         if 'shutdown' in printer_data:
#             # if RegisteredPrinter.objects.filter(printer_id=request.POST['printer_id']):
#             Printer.objects.filter(printer_id=printer_data['printer_id']).update(
#                 is_operational='False',
#                 is_printing='False',
#                 is_cancelling='False',
#                 is_closed_or_error='False',
#                 is_paused='False',
#                 is_pausing='False',
#                 is_ready='False',
#             )
#             return HttpResponse('goodbye')
#         elif 'startup' in printer_data:
#             print('connect from ', printer_data['plugin_id'])
#             return HttpResponse('welcome')
#         else:
#             if not RegisteredPrinter.objects.filter(printer_id=printer_data['printer_id']):
#                 return HttpResponse('打印机未注册')
#             else:
#                 Printer.objects.filter(printer_id=printer_data['printer_id']).update(
#                     is_operational=printer_data['is_operational'],
#                     is_printing=printer_data['is_printing'],
#                     is_cancelling=printer_data['is_cancelling'],
#                     is_closed_or_error=printer_data['is_closed_or_error'],
#                     is_paused=printer_data['is_paused'],
#                     is_pausing=printer_data['is_pausing'],
#                     is_ready=printer_data['is_ready'],
#                 )
#                 print('POST from', printer_data['printer_id'])
#                 try:
#                     # 查询是否有需要打印的gcode
#                     gcode_set = GcodeFile.objects.all()
#                     gcode_id = gcode_set.values('gcode_id').get(gcode_selected='True')['gcode_id']
#                     print("有文件需要打印")
#                     gcode_path = gcode_set.values('gcode_safepath').get(gcode_selected='True')['gcode_safepath']
#                     # print(gcode_path)
#                     gcode_name = gcode_set.values('gcode_name').get(gcode_selected='True')['gcode_name']
#                     # print(printer_state['is_operational'])
#
#                     if printer_data['is_ready'] == 'True':
#                         try:
#                             f = open(gcode_path, 'rb')
#                             r = FileResponse(f, as_attachment=True, filename=gcode_name)
#                             GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printed='True')
#                             GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='False')
#                             GcodeFile.objects.filter(gcode_id=gcode_id).update(
#                                 gcode_printer_id=printer_data['printer_id'])
#                             # 应该要remove
#                             return r
#                         except Exception:
#                             return Http404('error')
#                 except Exception:
#                     return HttpResponse('recieved')
#     if request.GET:
#         pass


# develop
def del_alldata(request):
    Printer.objects.all().delete()
    RegisteredPrinter.objects.all().delete()
    GcodeFile.objects.all().delete()
    return HttpResponse('数据库文件已删除')


def get_printer_state(request):
    if request.method == 'GET':
        printer_state = Printer.objects.all()
        return render(request, 'develop.html', context={'printer_state': printer_state})
