# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer

# 到时候全部models移到chat
from app.models import RegisteredPrinter, Printer, GcodeFile

# from channels.db import database_sync_to_async
from django.forms.models import model_to_dict


class PrinterConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        self.data = json.loads(text_data)

        octoprint_data = self.data.get('octoprint_data')
        octoprint_event = self.data.get('octoprint_event')

        current_print_ts = self.data.get('current_print_ts')
        tsd_gcode_file_id = self.data.get('tsd_gcode_file_id')

        print(self.data)
        print(self.data.keys())
        print(self.data.get('octoprint_data').keys())
        print(self.data.get('octoprint_event').keys())

        self.cmd_to_client = None
        self.msg_to_client = None
        self.data_to_client = None

        printer_state = octoprint_data.get('state').get('flags')

        if self.data.get('printer_state'):
            printer_state = self.data['printer_state']
            # print(printer_state)

            if not RegisteredPrinter.objects.filter(printer_id=printer_state['printer_id']):
                self.msg_to_client = '打印机未注册'
            else:
                Printer.objects.filter(printer_id=printer_state['printer_id']).update(
                    is_operational=printer_state['is_operational'],
                    is_printing=printer_state['is_printing'],
                    is_cancelling=printer_state['is_cancelling'],
                    is_closed_or_error=printer_state['is_closed_or_error'],
                    is_paused=printer_state['is_paused'],
                    is_pausing=printer_state['is_pausing'],
                    is_ready=printer_state['is_ready'],
                )
                self.msg_to_client = '打印机状态接收成功'

        # 查询是否有需要打印的gcode
        gcode_set = GcodeFile.objects.all()
        gcode_sel = gcode_set.filter(gcode_selected='True').first()

        # 查询第一个空闲的打印机
        printer_set = Printer.objects.all()
        printer_aval = printer_set.filter(is_ready='True').first()

        if gcode_sel:
            print("有文件需要打印")
            self.data_to_client = model_to_dict(gcode_sel)

            # 查询是否有打印机可用
            if printer_aval:
                self.cmd_to_client = 'print'
                # self.send(bytes_data=file)
                # GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printed='True')
                # GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='False')
                # GcodeFile.objects.filter(gcode_id=gcode_id).update(
                #    gcode_printer_id=printer_state['printer_id'])

        self.send(text_data=json.dumps(
            {
                'message': self.msg_to_client,
                'command': self.cmd_to_client,
                'data': self.data_to_client
            }))

    def disconnect(self, close_code):
        # Called when the socket close
        pass

# GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printed='True')
# GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='False')
# GcodeFile.objects.filter(gcode_id=gcode_id).update(
#    gcode_printer_id=printer_state['printer_id'])
