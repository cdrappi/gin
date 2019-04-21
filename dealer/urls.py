# todos/urls.py
from django.urls import path
from dealer import views

urlpatterns = [
    path('', views),
    # path('<int:pk>/', views.DetailTodo.as_view()),
]