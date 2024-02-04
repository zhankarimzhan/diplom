# myapp/urls.py

from django.urls import path
from app_d import views
from django.urls import path
# exams/urls.py
from django.urls import path
from .views import index, exam_detail, solve_test, upload_test


from django.urls import path
from .views import index, exam_detail, solve_test, upload_test, add_subject

from django.urls import path
from .views import solve_test
urlpatterns = [
    path('', views.pdf, name='upload_pdf'),
    path('exam', index, name='index'),
    path('exam/<int:subject_id>/', exam_detail, name='exam_detail'),
    path('solve/<int:qa_id>/', solve_test, name='solve_test'),
    path('upload/<int:subject_id>/', upload_test, name='upload_test'),
    path('add_subject/', add_subject, name='add_subject'),
    path('solve_test/<int:qa_id>/', solve_test, name='solve_test'),
]
