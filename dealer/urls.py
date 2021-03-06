from django.urls import path

from dealer import views

urlpatterns = [
    path('current_user/', views.current_user),
    path('users/', views.UserList.as_view()),
    path('games/', views.get_users_games),
    path('game_series/', views.get_users_game_series),
    path('draw/', views.draw_card),
    path('discard/', views.discard_card),
    path('create/', views.create_game_series),
]
