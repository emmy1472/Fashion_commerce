from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from django.contrib.auth import get_user_model
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

class CreateOrGetConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post (self, request):
        user = request.user
        other_user_id = request.data.get("user_id")

        if not other_user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        other_user = get_object_or_404(User, id=other_user_id)

        if other_user == user:
            return Response({"error": "cannot create conversation with yourself"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.filter(
            participants=user
        ).filter(participants=other_user).first()

        if conversation:
            return Response(ConversationSerializer(conversation).data)
        

        conversation = Conversation.objects.create()
        conversation.participants.add(user, other_user)

        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED
        )



class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response({"error": "you are not part of this conversation"}, status=status.HTTP_403_FORBIDDEN)
        
        text = request.data.get("text")
        if not text:
            return Response({"error": "message text is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text
        )

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    

class MessagePagination(PageNumberPagination):
    page_size = 25


class ListMessageView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        conversation = get_object_or_404(Conversation, id=self.kwargs.get("conversation_id"))
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("Unauthorized")
        return conversation.messages.order_by("timestamp")
    

class MarkAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in conversation.participants.all():
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        return Response({"message": "Messages marked as read"}, status=status.HTTP_200_OK)