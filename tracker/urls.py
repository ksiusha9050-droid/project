from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_session, name='start_session'),
    path('stop/', views.stop_session, name='stop_session'),
    path('check/<int:check_id>/', views.verify, name='verify'),
    path('history/', views.history, name='history'),
    path('history/<int:session_id>/', views.session_detail, name='session_detail'),
    path('stats/', views.stats, name='stats'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
