from django.urls import path
from .views import (
    CreateOrGetConversationView,
    SendMessageView,
    ListMessageView,
    MarkAsReadView,
)


urlpatterns = [
    path("conversation/", CreateOrGetConversationView.as_view(), name="create-get-conversation"),
    path("conversation/<int:conversation_id>/messages/", ListMessageView.as_view(), name="list-messages"),
    path("conversation/<int:conversation_id>/send/", SendMessageView.as_view(), name="send-messages"),
    
    path("conversation/<int:conversation_id>/read/", MarkAsReadView.as_view(), name="mark-as-read"),

]