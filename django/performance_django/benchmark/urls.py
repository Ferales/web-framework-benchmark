from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),

    path('register/', views.register, name='register'),

    path('login/', views.login, name='login'),

    path('upload_file/', views.upload_file, name='upload_file'),

    path('download_file/<int:file_id>/', views.get_file, name='download_file'),

    path('products/', views.get_products, name='get_products'),
    path('popular/', views.get_popular_products, name='get_popular_products'),
    path('orders/', views.get_orders, name='get_orders'),
]
