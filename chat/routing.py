# chat/routing.py
from django.urls import re_path, path

from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/printer', consumers.PrinterConsumer.as_asgi()),
# ]

websocket_urlpatterns = [
    path('ws/printer/', consumers.PrinterConsumer.as_asgi()),
    path('ws', consumers.PrintConsumer.as_asgi()),
]
