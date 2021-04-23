# chat/routing.py
from django.urls import re_path, path

from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/printer', consumers.PrinterConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    # 3d打印机控软件插件
    path('ws/printer/', consumers.PrinterConsumer.as_asgi()),
    #前端浏览器
    path('ws', consumers.PrintConsumer.as_asgi()),
]
