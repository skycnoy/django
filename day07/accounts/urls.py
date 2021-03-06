from django.urls import path, re_path
from accounts import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    re_path('pwdmod/(?P<pk>[0-9]{1,})?', views.UserPwdView.as_view(), name='pwdmod'),
    re_path('permmod/(?P<pk>[0-9]{1,})?', views.UserPermModView.as_view(), name='permmod'),
]