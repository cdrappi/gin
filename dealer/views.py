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
    user = request.user
    game = Game.new_game(user.id, request.POST['opponent_id'])
    action, parsed_game = game.parse_game(user)
    return JsonResponse(
        data={action: {game.id: parsed_game}}
    )


def get_games(request):
    """

    :param request:
    :return:
    """
    users_games = Game.list_users_games(request.user)
    return JsonResponse(data=users_games)
