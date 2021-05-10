from django.shortcuts import render, redirect

from app.models import GcodeFile, RegisteredPrinter, Command
from chat.models import Printer, Print

from django.http import FileResponse, JsonResponse, HttpResponse, Http404
from app.form import PrinterForm
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import os


# Create your views here:
# 主页面
@login_required
def printerlist(request):
    if request.method == 'GET':
        printer = RegisteredPrinter.objects.all()
        gcode = GcodeFile.objects.all()
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = None
        return render(request, 'list_websocket.html',
                      context={'printer': printer, 'gcode': gcode, 'username': username})


#注册打印机页面（使用ModelForm表单）
@login_required
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
            result = RegisteredPrinter.objects.filter(printer_id=printer_id)
            if not result:
                # 通过ModelForm表单创建RegisteredPrinter表的记录
                v.save()
                # 同时创建Printer表的记录，属性值为默认值
                Printer.objects.get_or_create(printer_id=printer_id)
            return redirect('/list_websocket/')
        else:
            error_msg = v.errors.as_json()
            return render(request, 'register_printer.html', locals())


#插件自动注册3d打印机
def register_printer_plugin(request):
    if request.method == 'POST':
        data = request.POST
        printer_id = data.get('printer_id', '')
        owner = data.get('owner', '')
        address = data.get('address', '')
        if printer_id and owner and address:
            if RegisteredPrinter.objects.filter(printer_id=printer_id):
                return HttpResponse('already')
            else:
                RegisteredPrinter.objects.get_or_create(printer_id=printer_id, owner=owner, address=address)
                Printer.objects.get_or_create(printer_id=printer_id)
                return HttpResponse('success')
        else:
            return HttpResponse('fail')


#删除打印机
@login_required
def del_printer(request):
    if request.method == 'POST':
        print_id = request.POST.get('printer_id', '')
        printer = RegisteredPrinter.objects.filter(printer_id=print_id)
        if printer:
            printer.delete()
            Printer.objects.filter(printer_id=print_id).delete()
            messages.success(request, '成功删除')
            return redirect('/list_websocket/')
        else:
            messages.error(request, '打印机不存在')
            return redirect('/list_websocket/')


#删除gcode
@login_required
def delgcodedata(request):
    if request.method == 'POST':
        gcode_id = request.POST.get('gcode_id', 0)
        gcode_file_sel = GcodeFile.objects.filter(pk=gcode_id).first()
        if gcode_file_sel:
            if gcode_file_sel.gcode_printing:
                messages.warning(request, '文件正在打印，请等待打印完成')
                return redirect('/list_websocket/')
            gcode_path = gcode_file_sel.gcode_safepath
            gcode_file_sel.delete()
            try:
                os.remove(gcode_path)
            except Exception:
                messages.error(request, 'gcode删除出错')
                return redirect('/list_websocket/')
            messages.success(request, '删除成功')
            return redirect('/list_websocket/')
        else:
            messages.error(request, '无gcode文件')
            return redirect('/list_websocket/')

    if request.method == 'GET':
        #因为只会有一个gcode文件
        gcode_file_sel = GcodeFile.objects.all().first()
        if gcode_file_sel:
            if gcode_file_sel.gcode_printing:
                messages.warning(request, '文件正在打印，请等待打印完成')
                return redirect('/list_websocket/')
            gcode_path = model_to_dict(gcode_file_sel)['gcode_safepath']
            gcode_file_sel.delete()
            try:
                os.remove(gcode_path)
            except Exception:
                messages.error(request, 'gcode文件删除出错')
                return redirect('/list_websocket/')

            messages.success(request, 'gcode文件删除成功')
            return redirect('/list_websocket/')
        else:
            messages.error(request, 'gcode文件删除出错')
            return redirect('/list_websocket/')


#下载gcode文件
def download_gcode_file(request, filename):
    if request.method == 'GET':
        #gcode文件所在文件夹
        gcode_folder = os.path.join(os.getcwd(), "gcodefiles")
        file_path = os.path.join(gcode_folder, filename)
        try:
            f = open(file_path, 'rb')
            r = FileResponse(f, as_attachment=True, filename=filename)
            return r
        except Exception:
            raise Http404('download error')


#上传gcode文件
@login_required
def upload_gcode_file(request):
    gcode_folder = os.path.join(os.getcwd(), "gcodefiles")
    if not os.path.exists(gcode_folder):
        os.makedirs(gcode_folder)

    if GcodeFile.objects.all().first():
        messages.warning(request, '已有文件上传，请先打印')
        return redirect('/list_websocket/')

    if request.method == 'POST':
        gcode_file_re = request.FILES.get("gcode_file", None)
        if not gcode_file_re:
            messages.error(request, '未选择文件')
            return redirect('/list_websocket/')
        else:
            gcode_path = os.path.join(gcode_folder, gcode_file_re.name)
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

        messages.success(request, '文件上传成功')
        return redirect('/list_websocket/')
    if request.method == 'GET':
        messages.error(request, 'no response')
        return redirect('/list_websocket/')


# 打印gcode
@login_required
def print_gcode(request):
    if request.method == 'POST':
        gcode_id = request.POST.get('gcode_id', '')
        gcode_file = GcodeFile.objects.filter(gcode_id=gcode_id)
        if gcode_file:
            gcode_file.update(gcode_selected='True')

        messages.success(request, '文件已选中，等待空闲打印机')
        return redirect('/list_websocket/')

    if request.method == 'GET':
        gcode_file_sel = GcodeFile.objects.all().first()
        if gcode_file_sel:
            gcode_id = gcode_file_sel.gcode_id
            gcode_file = GcodeFile.objects.filter(gcode_id=gcode_id)
            if gcode_file:
                gcode_file.update(gcode_selected='True')
            messages.success(request, '文件已选中，等待空闲打印机')
            return redirect('/list_websocket/')
        else:
            messages.error(request, '无gcode文件')
            return redirect('/list_websocket/')


@login_required
# 打印机控制
def cmd(request):
    # 选择第一个打印机（当前仅实现一个）
    printer = Printer.objects.all().first()
    if not printer:
        messages.error(request, '无打印机注册')
        return redirect('/list_websocket/')
    elif not printer.operational:
        messages.error(request, '打印机未连接或不可用')
        return redirect('/list_websocket/')
    elif printer.closedOrError:
        messages.error(request, '打印机关闭或错误')
        return redirect('/list_websocket/')
    else:
        command = Command.objects.get_or_create(printer_id=printer.printer_id)[0]

    if request.method == 'POST':
        cmd = request.POST.get('cmd', '')
        # print(cmd)
        # print(type(command))

        if cmd == "回零" and printer.ready:
            command.home = True
            command.save()
            messages.success(request, '命令已发出')
            return redirect('/list_websocket/')

        if cmd == "暂停打印" and printer.printing:
            command.pause = True
            command.save()
            messages.success(request, '命令已发出')
            return redirect('/list_websocket/')

        if cmd == "继续打印" and printer.paused:
            command.resume = True
            cmd.save()
            messages.success(request, '命令已发出')
            return redirect('/list_websocket/')

        if cmd == "取消打印" and printer.printing:
            command.cancel = True
            command.save()
            messages.success(request, '命令已发出')
            return redirect('/list_websocket/')

        else:
            messages.warning(request, '无效命令')
            return redirect('/list_websocket/')


# 开发测试用
def del_alldata(request):
    Printer.objects.all().delete()
    RegisteredPrinter.objects.all().delete()
    GcodeFile.objects.all().delete()
    Print.objects.all().delete()
    Command.objects.all().delete()
    return HttpResponse('数据库文件已删除')


def get_all_model(request):
    if request.method == 'GET':
        printer_state = Printer.objects.all()
        gcodefile = GcodeFile.objects.all()
        print_job = Print.objects.all()
        return render(request, 'develop.html', locals())

def delprinterdata(request):
    Printer.objects.all().delete()
    return redirect('/list_websocket/')
