from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Follow
from .serializers import FollowSerializer
from accounts.serializers import UserListSerializer
from accounts.models import User

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if request.user == target_user:
            return Response({"error": "you cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )

        if not created:
            return Response({"message": "Already following this user."}, status=status.HTTP_200_OK)

        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class UnfollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        follow = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).first()

        if not follow:
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)
        
        follow.delete()
        return Response({"message": "Successfully unfollowed the user."}, status=status.HTTP_200_OK)
    

class FollowersListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        followers_qs = user.followers.select_related('follower').all().order_by('-created_at')
        users = [f.follower for f in followers_qs]
        serializer = UserListSerializer(users, many=True, context={'request': request})
        return Response({'count': followers_qs.count(), 'results': serializer.data}, status=status.HTTP_200_OK)
    

class FollowingListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        following_qs = user.following.select_related('following').all().order_by('-created_at')
        users = [f.following for f in following_qs]
        serializer = UserListSerializer(users, many=True, context={'request': request})
        return Response({'count': following_qs.count(), 'results': serializer.data}, status=status.HTTP_200_OK)
