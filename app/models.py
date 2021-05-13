from django.db import models
from django.contrib.auth.models import User


# 注册3d打印机信息表
class RegisteredPrinter(models.Model):
    printer_id = models.CharField(max_length=100, primary_key=True)

    # owner = models.CharField(max_length=20)

    address = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)


# Printer状态信息表
class Printer(models.Model):
    printer_id = models.CharField(max_length=100, primary_key=True)

    current_print = models.OneToOneField(to='Print', on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='not_used')

    operational = models.BooleanField(null=False, blank=False, default=False)
    printing = models.BooleanField(null=False, blank=False, default=False)
    cancelling = models.BooleanField(null=False, blank=False, default=False)
    pausing = models.BooleanField(null=False, blank=False, default=False)
    resuming = models.BooleanField(null=False, blank=False, default=False)
    finishing = models.BooleanField(null=False, blank=False, default=False)
    closedOrError = models.BooleanField(null=False, blank=False, default=True)
    error = models.BooleanField(null=False, blank=False, default=False)
    paused = models.BooleanField(null=False, blank=False, default=False)
    ready = models.BooleanField(null=False, blank=False, default=False)

    tool0_temperature = models.IntegerField(null=True, blank=True, default=0)
    tool1_temperature = models.IntegerField(null=True, blank=True, default=0)
    bed_temperature = models.IntegerField(null=True, blank=True, default=0)


# 打印任务表
class Print(models.Model):
    # 级联删除gcodefile
    gcodefile = models.OneToOneField(to='GcodeFile',
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name='print',
                                     primary_key=True)

    # 预计打印时间
    estimatedPrintTime = models.IntegerField(null=True, blank=True, default=0)

    # averagePrintTime = models.IntegerField(null=True, blank=True, default=0)

    # 当前打印作业的完成百分比
    completion = models.FloatField(null=True, blank=True, default=0)
    # 已花费的打印时间
    printTime = models.IntegerField(null=True, blank=True, default=0)
    # 估计剩余打印时间，以秒为单位
    printTimeLeft = models.IntegerField(null=True, blank=True, default=0)


# gcode文件信息表表
class GcodeFile(models.Model):
    gcode_id = models.AutoField(primary_key=True)
    gcode_name = models.CharField(max_length=100)
    gcode_url = models.URLField(max_length=100)
    gcode_safepath = models.CharField(max_length=100)

    gcode_printed = models.BooleanField(default=False)
    gcode_selected = models.BooleanField(default=False)
    gcode_printing = models.BooleanField(default=False)

    # gcode_printer_id = models.CharField(max_length=100, blank=True, null=True, default='no')

    gcode_printfailed = models.BooleanField(default=False)


# command
class Command(models.Model):
    printer_id = models.CharField(max_length=100, primary_key=True)
    print = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)
    resume = models.BooleanField(default=False)
    pause = models.BooleanField(default=False)
    home = models.BooleanField(default=False)
