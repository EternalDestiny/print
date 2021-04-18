from django.urls import path
from . import views

urlpatterns = [

    # 打印机列表
    path('list/', views.printerlist),

    path('list/register_printer/', views.register_printer),

    path('list/del_printer/', views.del_printer),

    # api
    path('list/ajax_printer_state/', views.printerlist_api),

    path('list/ajax_print_event/', views.print_api),

    # 文件
    path('download_gcode_file/<str:filename>/', views.download_gcode_file, name='downloaded'),

    path('list/upload_gcode_file/', views.upload_gcode_file, name='uploaded'),
    path('list/delgcodedata/', views.delgcodedata, name='delete'),
    path('list/printgcode/', views.print_gcode, name='print'),

    # path('test/', views.test, name='test'),

    # develop
    path('develop/del_alldata/', views.del_alldata),
    path('develop/printer_state/', views.get_printer_state),

]
