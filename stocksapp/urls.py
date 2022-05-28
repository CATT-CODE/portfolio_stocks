from django.urls import path, include
from . import views


app_name = 'stocksapp'
urlpatterns = [
	path('', views.charts, name='charts'),
	path('login/', views.login, name='login'),
	path('signup/', views.signup, name='signup'),
	path('logout/', views.logOut, name='logOut'),
	# path('test/', views.test, name='test'),
]