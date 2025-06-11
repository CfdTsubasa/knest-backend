from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/circle/(?P<circle_id>[^/]+)/chat/$', consumers.CircleChatConsumer.as_asgi()),
] 