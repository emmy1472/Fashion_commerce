from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer
from django.shortcuts import get_object_or_404


class CreatePostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data, context= {'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListPostsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        post = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserPostsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(user=request.user)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        like = Like.objects.filter(user=user, post=post).first()

        if like:
            like.delete()
            return Response({
                "message": "Post unliked", "likes_count": post.likes.count()},
                status=status.HTTP_200_OK)
        
        Like.objects.create(user=user, post=post)
        return Response({
            "message": "Post liked",
            "likes_count": post.likes.count()
        }, status=status.HTTP_201_CREATED)
    

class AddCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        content = request.data.get("content")
        if not content:
            return Response({"error": "Comment text is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            content=content
        )

        return Response({
            "message": "Comment added",
            "comment": CommentSerializer(comment).data,
            "comments_count": post.comments.count()
        }, status=status.HTTP_201_CREATED)
    
class ListCommentsView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.order_by("-created_at")

        serialized = CommentSerializer(comments, many=True)
        return Response({
            "post_id": post.id,
            "total_comments": comments.count(),
            "comments": serialized.data
        })