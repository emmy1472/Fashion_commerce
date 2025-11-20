from django.urls import path
from .views import CreatePostsView, ListPostsView, UserPostsView, ToggleLikeView, AddCommentView, ListCommentsView


urlpatterns = [
    path('create/', CreatePostsView.as_view(), name='create-posts'),
    path('', ListPostsView.as_view(), name='list-posts'),
    path('me', UserPostsView.as_view(), name='user-posts'),
    path("<int:post_id>/like/", ToggleLikeView.as_view(), name="toggel-like"),
    path("<int:post_id>/comment/", AddCommentView.as_view(), name="add-comment"),
    path("<int:post_id>/comments/", ListCommentsView.as_view(), name="list-comments"),
]