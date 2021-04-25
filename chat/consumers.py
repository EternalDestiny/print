# chat/consumers.py
import json
import time
import datetime
from channels.generic.websocket import WebsocketConsumer
import threading

from app.models import RegisteredPrinter, GcodeFile
from .models import Print, Printer

# from channels.db import database_sync_to_async
from django.forms.models import model_to_dict
from django.db.models import Q


# 与3d打印机控制软件插件的websocket
class PrinterConsumer(WebsocketConsumer):
    def connect(self):
        # 在这里添加plugin连接的验证信息，验证成功才能连接，本系统尚未实现
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        # print(data)
        # print(data.keys())
        # print(data.get('octoprint_data').keys())
        # print(data.get('octoprint_event').keys()

        self.process_printer_data(data)

    def disconnect(self, close_code):
        # ws连接结束后需要做什么，可以考虑
        pass

    def process_printer_data(self, data):

        printer_id = data.get('printer_id', {})
        octoprint_data = data.get('octoprint_data', {})

        # 打印机未连接，温度数据为空
        temperatures = data.get('temperatures', {})

        # 打印机事件
        octoprint_event = data.get('octoprint_event', {})

        # 打印开始后开始有gcode_id
        gcode_id = data.get('gcode_id', {})

        # current_print_ts = data.get('current_print_ts')

        # 打印机状态
        printer_state = octoprint_data.get('state', {}).get('flags', {})
        #打印工作
        job = octoprint_data.get('job', {})
        #打印进度
        progress = octoprint_data.get('progress', {})

        if RegisteredPrinter.objects.filter(printer_id=printer_id):
            printer = Printer.objects.filter(printer_id=printer_id)
            #更新打印机状态
            if printer_state:
                printer_state.__delitem__('sdReady')
                printer.update(**printer_state)
                self.send_data_to_client(message='打印机状态接收成功')
            if temperatures:
                printer.update(tool0_temperature=temperatures.get('tool0', {}).get('actual', 0))
                printer.update(tool1_temperature=temperatures.get('tool1', {}).get('actual', 0))
                printer.update(bed_temperature=temperatures.get('bed', {}).get('actual', 0))

            # 查询是否有需要打印的gcode
            gcode_set = GcodeFile.objects.all()
            # gcode_sel = gcode_set.filter(~Q(gcode_printer_id='no'),gcode_selected='True').first()
            gcode_sel = gcode_set.filter(gcode_selected=True).first()

            # 查询第一个空闲的打印机
            printer_set = Printer.objects.all()

            # 仅仅ready无法判断是否有模型未取下，需要人工，这里简化处理
            printer_aval = printer_set.filter(ready=True).first()

            if gcode_sel:
                print("有文件需要打印")
                # 查询是否有打印机可用
                if printer_aval:
                    self.send_data_to_client(message='打印任务已下发',
                                             command='print',
                                             data=model_to_dict(gcode_sel)
                                             )

            # octoprint_event有：PrintDone、PrintFailed、PrintStarted
            if gcode_id and octoprint_event:
                event_type = octoprint_event.get('event_type', {})
                print("*******" + event_type)
                gcode_file = GcodeFile.objects.filter(gcode_id=gcode_id).first()
                # print(octoprint_event)

                # 数据库有打印工作时，更新状态
                print_job = Print.objects.filter(gcodefile=gcode_file).first()
                if print_job:
                    print_job.update(estimatedPrintTime=job.get('estimatedPrintTime', 0),
                                     # averagePrintTime=job.get('averagePrintTime',0),
                                     completion=progress.get('completion', 0),
                                     printTime=progress.get('printTime', 0),
                                     printTimeLeft=progress.get('printTimeLeft', 0),
                                     )
                # 打印任务开始时
                if event_type == 'PrintStarted':
                    # 更新gcode_file表
                    gcode_file.gcode_printer_id = printer_aval.printer_id
                    gcode_file.save()

                    gcode_file.update(gcode_selected=False)
                    gcode_file.update(gcode_printing=True)

                    # 新建一个Print工作
                    print_job = Print(gcodefile=gcode_file)
                    print_job.save()

                # 打印任务结束时
                if event_type == 'PrintDone':
                    # 更新gcode_file表
                    gcode_file.update(gcode_printed=True)

                # 打印失败时
                # 更新gcode_file表
                if event_type == 'PrintFailed':
                    gcode_file.update(gcode_printfailed=True)
                    gcode_file.update(gcode_printing=False)

        else:
            self.send_data_to_client(message='打印机未注册')

    #传输给客户端的数据
    def send_data_to_client(self, message=None, command=None, data=None):
        self.send(text_data=json.dumps(
            {
                'message': message,
                'command': command,
                'data': data,
            }))


#与前端网页的websocket，负责推送数据
class PrintConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.close = False
        self.send_loop_thread = threading.Thread(target=self.send_loop)
        self.send_loop_thread.daemon = True
        self.send_loop_thread.start()

    def receive(self, text_data=None, bytes_data=None):
        pass

    def disconnect(self, close_code):
        self.close = True
        # Called when the socket close

    def send_loop(self):
        data = {}
        while True:
            if self.close:
                return
            time.sleep(1)
            # 发送两种数据给前端
            # 打印机状态
            data.update(self.get_printer_state())
            # 打印进度（包括当前温度）
            data.update(self.get_print_progress())
            # print(data)
            self.send(json.dumps(data))

    #从数据库中获得打印机状态信息
    def get_printer_state(self):
        printer_list = {}
        printer = Printer.objects.all()

        for p in printer:
            if p.ready:
                state = '在线，可供打印'
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
        if printer_list:
            return {'printer_state': printer_list}
        else:
            return {'printer_state': '当前无打印机注册'}

    # 从数据库中获得打印进度信息
    def get_print_progress(self):
        # 当前仅实现一个任务
        print = Print.objects.all().first()
        # for print_job in print:
        data = {}
        if print:
            estimatedPrintTime = str(datetime.timedelta(seconds=print.estimatedPrintTime))
            completion = format(print.completion / 100, '.0%')
            printTime = str(datetime.timedelta(seconds=print.printTime))
            printTimeLeft = str(datetime.timedelta(seconds=print.printTimeLeft))

            print_progress = {'estimatedPrintTime': estimatedPrintTime,
                              'completion': completion,
                              'printTime': printTime,
                              'printTimeLeft': printTimeLeft, }

            data['print_progress'] = print_progress

            printer_id = print.printer_id
            printer = Printer.objects.filter(printer_id=printer_id).first()
            temperatures = model_to_dict(printer,
                                         fields=['tool0_temperature', 'tool1_temperature',
                                                 'bed_temperature', ])
            data['temperatures'] = temperatures

        else:
            data = {'print_progress': {'estimatedPrintTime': '无数据',
                                       'completion': '无数据',
                                       'printTime': '无数据',
                                       'printTimeLeft': '无数据'},
                    'temperatures': {'tool0_temperature': '无数据',
                                     'tool1_temperature': '无数据',
                                     'bed_temperature': '无数据', }}

        return data
