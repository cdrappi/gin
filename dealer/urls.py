# todos/urls.py
from django.urls import path
from dealer import views

urlpatterns = [
    path('users', views.list_users),
    # path('<int:pk>/', views.DetailTodo.as_view()),
]