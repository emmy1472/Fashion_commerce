from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from django.contrib.auth import get_user_model
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()

class CreateOrGetConversationView(APIView):
    def post (self, request):
        user = request.user
        other_user_id = request.data.get("user_id")

        if not other_user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        other_user = get_object_or_404(User, id=other_user_id)

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
    

class ListMessageView(APIView):
    def get(self, request, conversation_id):
        conversation = get_object_or_404(conversation, id=conversation_id)

        if request.user not in conversation.participatnts.all():
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        messages = conversation.messages.order_bu("timestamp")
        return Response(MessageSerializer(messages, many=True).data)