from django import forms
from app.models import RegisteredPrinter, GcodeFile, Print, Printer

# 注册打印机使用ModelForm表单
class PrinterForm(forms.ModelForm):
    class Meta:
        model = RegisteredPrinter
        fields = '__all__'

        labels = {
            'pritner_id': 'pritner_id',
            'owner': '打印机所有者',
            'address': '打印机所在位置',
        }

        help_texts = {
            'printer_id': '请输入打印机的唯一标识符',
            'owner': '请输入登录用户名'
        }

        error_messages = {
            '__all__': {'required': '请输入内容', 'invalid': '请检查输入内容'},
        }