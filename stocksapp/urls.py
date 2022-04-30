from django.urls import path
from . import views

app_name = 'stocksapp'
urlpatterns = [
	path('', views.home, name='home'),
]