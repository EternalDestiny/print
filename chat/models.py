from django.db import models
from app.models import GcodeFile


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
    tool2_temperature = models.IntegerField(null=True, blank=True, default=0)
    bed_temperature = models.IntegerField(null=True, blank=True, default=0)

    # class _meta:
    #     abstract = True
    #     ordering = ['printer_id']


class Print(models.Model):
    # 级联删除gcodefile
    gcodefile = models.OneToOneField(to=GcodeFile,
                                     on_delete=models.CASCADE,
                                     null=False,
                                     blank=False,
                                     related_name='print',
                                     primary_key=True)

    estimatedPrintTime = models.IntegerField(null=True, blank=True, default=0)

    # averagePrintTime = models.IntegerField(null=True, blank=True, default=0)

    # 当前打印作业的完成百分比
    completion = models.FloatField(null=True, blank=True, default=0)
    # 已花费的打印时间
    printTime = models.IntegerField(null=True, blank=True, default=0)
    # 估计剩余打印时间，以秒为单位
    printTimeLeft = models.IntegerField(null=True, blank=True, default=0)
