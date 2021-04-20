# chat/consumers.py
import json
import time
from channels.generic.websocket import WebsocketConsumer
import threading

# 到时候全部models移到chat
from app.models import RegisteredPrinter, GcodeFile
from .models import Print, Printer

# from channels.db import database_sync_to_async
from django.forms.models import model_to_dict
from django.db.models import Q


class PrinterConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        self.data = json.loads(text_data)

        # print(self.data)
        # print(self.data.keys())
        # print(self.data.get('octoprint_data').keys())
        # print(self.data.get('octoprint_event').keys())

        printer_id = self.data.get('printer_id', {})
        gcode_id = self.data.get('gcode_id', {})

        octoprint_data = self.data.get('octoprint_data', {})
        octoprint_event = self.data.get('octoprint_event', {})

        # current_print_ts = self.data.get('current_print_ts')
        printer_state = octoprint_data.get('state', {}).get('flags', {})

        if RegisteredPrinter.objects.filter(printer_id=printer_id):
            if printer_state:
                printer_state.__delitem__('sdReady')
                Printer.objects.filter(printer_id=printer_id).update(**printer_state)
                self.send_data_to_client(message='打印机状态接收成功')

            # 查询是否有需要打印的gcode
            gcode_set = GcodeFile.objects.all()
            # gcode_sel = gcode_set.filter(~Q(gcode_printer_id='no'),gcode_selected='True').first()
            gcode_sel = gcode_set.filter(gcode_selected='True').first()
            # 查询第一个空闲的打印机
            printer_set = Printer.objects.all()
            printer_aval = printer_set.filter(ready='True').first()

            if gcode_sel:
                print("有文件需要打印")
                # 查询是否有打印机可用
                if printer_aval:
                    self.send_data_to_client(message='打印任务已下发',
                                             command='print',
                                             data=model_to_dict(gcode_sel)
                                             )

                    # 更新print数据库和gcode数据库
                    gcode_sel.gcode_printer_id = printer_aval.printer_id
                    gcode_sel.save()

                    print_job = Print(gcodefile=gcode_sel)
                    print_job.save()

            if gcode_id and octoprint_event:
                self.process_printer_event(octoprint_data, octoprint_event, gcode_id, printer_id)

        else:
            self.send_data_to_client(message='打印机未注册')

    def disconnect(self, close_code):
        # Called when the socket close
        pass

    def send_data_to_client(self, message=None, command=None, data=None):
        self.send(text_data=json.dumps(
            {
                'message': message,
                'command': command,
                'data': data,
            }))

    def process_printer_event(self, octoprint_data, octoprint_event, gcode_id, printer_id):
        # 更新gcode和Print数据库
        job = octoprint_data.get('job', {})
        progress = octoprint_data.get('progress', {})
        if octoprint_event.get('event_type') == 'PrintStarted':
            gcode_file = GcodeFile.objects.filter(gcode_id=gcode_id)
            gcode_file.update(gcode_printing=True)

            print_job = Print.objects.filter(gcodefile=gcode_file)
            print_job.update(estimatedPrintTime=job.get('estimatedPrintTime'),
                             averagePrintTime=job.get('averagePrintTime'),
                             completion=progress.get('completion'),
                             printTime=progress.get('printTime'),
                             printTimeLeft=progress.get('printTimeLeft'),
                             )

        if octoprint_event.get('event_type') == 'PrintDone':
            gcode_file = GcodeFile.objects.filter(gcode_id=gcode_id)
            gcode_file.update(gcode_printed=True)


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
            time.sleep(2)
            data.update(self.get_printer_state())
            data.update(self.get_print_progress())
            # print(data)
            self.send(json.dumps(data))

    def get_printer_state(self):
        printer_list = {}
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
        if printer_list:
            return {'printer_state': printer_list}
        else:
            return {'printer_state': '当前无打印机注册'}

    def get_print_progress(self):
        print = Print.objects.all().first()
        # 当前仅实现一个
        # for print_job in print:
        if print:
            print_job = {'print_progress:': model_to_dict(print,
                                                          fields=['estimatedPrintTime', 'averagePrintTime',
                                                                  'completion', 'printTime', 'printTimeLeft', ])}
        else:
            print_job = {'print_progress': '当前无任务'}

        return print_job
