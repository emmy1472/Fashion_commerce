from django.urls import path
from .views import FollowUserView, UnfollowUserView, FollowersListView, FollowingListView


urlpatterns = [
    path('<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('<int:user_id>/unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    path('<int:user_id>/followers/', FollowingListView.as_view(), name='list-followers'),
    path('<int:user_id>/following/', FollowingListView.as_view(), name='list-following'),
]   