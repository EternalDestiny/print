# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
# 到时候全部models移到chat
from app.models import RegisteredPrinter, Printer, GcodeFile
from channels.db import database_sync_to_async
from django.forms.models import model_to_dict


class PrinterConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        cmd = None
        msg = None
        args = None
        if text_data_json.get('printer_state'):
            printer_state = text_data_json['printer_state']
            # print(printer_state)

            if not RegisteredPrinter.objects.filter(printer_id=printer_state['printer_id']):
                msg = '打印机未注册'
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
                msg = '打印机状态接收成功'

        # 查询是否有需要打印的gcode
        gcode_set = GcodeFile.objects.all()
        gcode_sel = gcode_set.filter(gcode_selected='True').first()

        printer_set = Printer.objects.all()
        printer_aval = printer_set.filter(is_ready='True').first()

        if gcode_sel:
            print("有文件需要打印")
            gcode_id = gcode_sel.gcode_id
            gcode_path = gcode_sel.gcode_safepath
            # print(gcode_path)
            gcode_name = gcode_sel.gcode_name
            args = model_to_dict(gcode_sel)

            # 查询是否有打印机可用
            if printer_aval:
                try:
                    # file = open(gcode_path, 'rb')
                    cmd = 'print'
                    # self.send(bytes_data=file)
                    # GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_printed='True')
                    # GcodeFile.objects.filter(gcode_id=gcode_id).update(gcode_selected='False')
                    # GcodeFile.objects.filter(gcode_id=gcode_id).update(
                    #    gcode_printer_id=printer_state['printer_id'])
                except Exception:
                    msg = '文件服务器出错'

        self.send(text_data=json.dumps({'message': msg, 'commands': {'cmd': cmd, 'args': args}}))

    def disconnect(self, close_code):
        # Called when the socket close
        pass
