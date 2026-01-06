from django.urls import path
from .views import (
    PostsListCreateView,
    UserPostsView,
    ToggleLikeView,
    AddCommentView,
    ListCommentsView,
    PostDetailView,
)


urlpatterns = [
    path('', PostsListCreateView.as_view(), name='list-create-posts'),
    path('me/', UserPostsView.as_view(), name='user-posts'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_id>/like/', ToggleLikeView.as_view(), name='toggle-like'),
    path('<int:post_id>/comment/', AddCommentView.as_view(), name='add-comment'),
    path('<int:post_id>/comments/', ListCommentsView.as_view(), name='list-comments'),
]