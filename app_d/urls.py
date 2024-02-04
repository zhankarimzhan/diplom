# myapp/urls.py

from django.urls import path
from app_d import views
from django.urls import path
urlpatterns = [
    path('', views.pdf, name='upload_pdf'),
    
]
