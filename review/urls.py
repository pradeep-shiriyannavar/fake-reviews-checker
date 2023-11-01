from django.urls import path
from . import views
urlpatterns=[
    path('',views.index,name='index'),
    path('extract_review', views.extract_review, name='extract_review'),
    path('signup',views.signup, name='signup'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path('check', views.check, name='check')
]