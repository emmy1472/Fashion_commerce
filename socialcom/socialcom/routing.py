from channels.routing import ProtocolTypeRouter, URLRouter
from ..messaging.middleware import JWTAuthMiddleware
from django.urls import path
from ..messaging import consumers


websocket_urlpatterns = [
    path("ws/chat/<int:conversation_id>/", consumers.ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    )
})