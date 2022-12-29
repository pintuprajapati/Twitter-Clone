from django.urls import path
from .views import *
urlpatterns = [
    path('latest-posts/', PostListView.as_view(), name='latest-post-list'),
    path('my-posts/', my_posts, name='my-post-list'),
    path('post/<int:pk>', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(), name='comment-delete'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'), 
    path('error/', error_view, name='error-page'), 
]