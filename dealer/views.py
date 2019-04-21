from django.contrib.auth.models import User
from django.http.response import JsonResponse

from dealer.models import Game


def list_users(request):
    """

    :param request:
    :return:
    """
    all_users = User.objects.all().values('id', 'email')
    return JsonResponse(data=list(all_users))


def create_game(request):
    """

    :param request:
    :return:
    """
    player_1_id = request.POST['player_1_id']
    player_2_id = request.POST['player_2_id']
    game = Game.new_game(player_1_id, player_2_id)
    return JsonResponse(
        data={
            'game_id': game.id,
            'hand': game.p1_hand,
            'top_card': game.top_card,
        }
    )


def get_games(request):
    """

    :param request:
    :return:
    """
    users_games = Game.list_users_games(request.user)
    return JsonResponse(data=users_games)
