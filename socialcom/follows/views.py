from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Follow
from .serializers import FollowSerializer
from accounts.models import User

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)

        if request.user == target_user:
            return Response({"error": "you cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            followers = request.user,
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
        followers= user.followers.all().select_related("follower")
        data = [{"id": f.follower.id, "username": f.follower.username} for f in followers]
        return Response(data, status=status.HTTP_200_OK)
    

class FollowingListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        following = user.following.all().select_related("following")
        data = [{"id": f.following.id, "username": f.following.username} for f in following]
        return Response(data, status=status.HTTP_200_OK)
