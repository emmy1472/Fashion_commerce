from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from .permissions import IsOwnerOrReadOnly


class PostsListCreateView(generics.ListCreateAPIView):
    """List all posts (paginated) and allow authenticated users to create posts."""
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserPostsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-created_at')


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_update(self, serializer):
        # `IsOwnerOrReadOnly` ensures only owner may update; just save
        serializer.save()

    def perform_destroy(self, instance):
        # `IsOwnerOrReadOnly` ensures only owner may delete
        instance.delete()


class ToggleLikeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        like = Like.objects.filter(user=user, post=post).first()

        if like:
            like.delete()
            return Response({"message": "Post unliked", "likes_count": post.likes.count()}, status=status.HTTP_200_OK)

        Like.objects.create(user=user, post=post)
        return Response({"message": "Post liked", "likes_count": post.likes.count()}, status=status.HTTP_201_CREATED)


class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(user=self.request.user, post=post)


class ListCommentsView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments.order_by('-created_at')