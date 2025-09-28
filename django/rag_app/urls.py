# rag_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.rag_query, name='rag_query'),
]