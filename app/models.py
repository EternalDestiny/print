from django.db import models


# Create your models here.
class Printer(models.Model):
    printer_id = models.CharField(max_length=100, primary_key=True)
    is_operational = models.CharField(max_length=10, default='False')
    is_printing = models.CharField(max_length=10, default='False')
    is_cancelling = models.CharField(max_length=10, default='False')
    is_closed_or_error = models.CharField(max_length=10, default='False')
    is_paused = models.CharField(max_length=10, default='False')
    is_pausing = models.CharField(max_length=10, default='False')
    is_ready = models.CharField(max_length=10, default='False')
    # class _meta:
    #     abstract = True
    #     ordering = ['printer_id']



class RegisteredPrinter(models.Model):
    printer_id=models.CharField(max_length=100, primary_key = True)
    owner=models.CharField(max_length=20)
    address=models.CharField(max_length=20)

class GcodeFile(models.Model):
    gcode_id = models.AutoField(primary_key=True)
    gcode_name = models.CharField(max_length=100)
    gcode_url = models.URLField(max_length=100)
    gcode_safepath = models.CharField(max_length=100)
    gcode_printed = models.CharField(max_length=10)
    gcode_selected = models.CharField(max_length=10)
    gcode_printer_id = models.CharField(max_length=100, blank=True)
