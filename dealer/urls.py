# todos/urls.py
from django.urls import path

from dealer import views

urlpatterns = [
    # path('users', views.list_users),
    path('games', views.get_users_games),
    path('create', views.create_game),
    path('draw', views.draw_card),
    path('discard', views.discard_card),
    path('current_user/', views.current_user),
    path('users/', views.UserList.as_view()),
]
