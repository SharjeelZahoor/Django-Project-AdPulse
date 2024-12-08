
from django.urls import path
from . import views
from .views import custom_logout
app_name = 'ads'
urlpatterns = [
    path('', views.AdListView.as_view(), name='ad_list'),
    path('ads/', views.AdListView.as_view(), name='ad_list'),
    path('ad/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ads/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    path('picture/<int:pk>/', views.ad_picture, name='ad_picture'),
    path('ad/<int:pk>/comment/', views.CommentCreateView.as_view(), name='ad_comment_create'),
    path ('ad/<int:pk>/comment/delete/', views.CommentDeleteView.as_view(), name='ad_comment_delete'),
    path('ad/<int:pk>/favorite/', views.AddFavoriteView.as_view(), name='ad_favorite'),
    path('ad/<int:pk>/unfavorite/', views.DeleteFavoriteView.as_view(), name='ad_unfavorite'),


    path('logout/', custom_logout, name='logout'),
]
