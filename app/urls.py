from django.urls import path
from . import views

urlpatterns = [

    # 主页面
    path('list_websocket/', views.printerlist),

    # 注册、删除打印机
    path('register_printer/', views.register_printer),
    path('regiser_printer_plugin/', views.register_printer_plugin),
    path('del_printer/', views.del_printer),

    # 上传、删除、打印gcode
    path('upload_gcode_file/', views.upload_gcode_file, name='uploaded'),
    path('delgcodedata/', views.delgcodedata, name='delete'),
    path('printgcode/', views.print_gcode, name='print'),

    # gcode文件URL
    path('download_gcode_file/<str:filename>/', views.download_gcode_file, name='downloaded'),

    # develop（开发、测试）
    path('develop/del_alldata/', views.del_alldata),
    path('develop/all_data/', views.get_all_model),

]
