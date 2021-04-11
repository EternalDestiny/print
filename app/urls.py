from django.urls import path
from . import views

urlpatterns = [

    path('', views.getresponse),

    # 计算
    path('calpage/', views.calpage),
    path('result/', views.calculate),

    # 打印机列表
    path('list/', views.printerlist),
    path('list/ajax/', views.printerlist_api),
    path('list/test/', views.printerlist_api),
    path('list/register_printer/', views.register_printer),
    path('list/del_printer', views.del_printer),

    # 下载文件
    path('download/', views.downloadindex, name='download'),
    path('download/download1', views.download1, name='download1'),

    path('download_gcode_file/<str:filename>/', views.download_gcode_file, name='downloaded'),

    path('upload_gcode_file/', views.upload_gcode_file, name='uploaded'),

    path('list/upload_gcode_file/', views.upload_gcode_file, name='uploaded'),
    path('list/delgcodedata/', views.delgcodedata, name='delete'),
    path('list/printgcode/', views.print_gcode, name='print'),

    path('test/', views.test, name='test'),

]
