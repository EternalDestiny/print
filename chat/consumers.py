# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer

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

        print(self.data)
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
