from django.db import models


# 注册3d打印机信息表
class RegisteredPrinter(models.Model):
    printer_id = models.CharField(max_length=100, primary_key=True)
    owner = models.CharField(max_length=20)
    address = models.CharField(max_length=20)


#gcode文件信息表表
class GcodeFile(models.Model):
    gcode_id = models.AutoField(primary_key=True)
    gcode_name = models.CharField(max_length=100)
    gcode_url = models.URLField(max_length=100)
    gcode_safepath = models.CharField(max_length=100)

    gcode_printed = models.BooleanField(default=False)
    gcode_selected = models.BooleanField(default=False)
    gcode_printing = models.BooleanField(default=False)

    gcode_printer_id = models.CharField(max_length=100, blank=True, null=True, default='no')

    gcode_printfailed = models.BooleanField(default=False)
