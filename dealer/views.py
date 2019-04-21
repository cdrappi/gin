from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponseBadRequest

from dealer.models import Game


def list_users(request):
    """

    :param request:
    :return:
    """
    all_users = [
        user
        for user in User.objects.all().values('id', 'email')
        # list all potential opponents
        if user['id'] != request.user.id
    ]
    return JsonResponse(data=list(all_users), safe=False)


def create_game(request):
    """

    :param request:
    :return:
    """
    user = request.user
    game = Game.new_game(user.id, request.POST['opponent_id'])
    return JsonResponse(data=game.state_dict(user))


def get_users_games(request):
    """

    :param request:
    :return:
    """
    users_games = Game.list_users_games(request.user)
    return JsonResponse(data=users_games)


def draw_card(request):
    """

    :param request:
    :return:
    """
    user = request.user
    game = Game.objects.get(id=request.GET['game_id'])
    action = game.get_action(user)
    if action != Game.DRAW:
        return HttpResponseBadRequest(f"Can't {Game.DRAW}. Please {action}")

    if request.GET['from_discard'] == 'true':
        game.draw_top_card(user)
    else:
        game.draw_random_card(user)

    return JsonResponse(data=game.state_dict(user))


def discard_card(request):
    """

    :param request:
    :return:
    """
    user = request.user
    game = Game.objects.get(id=request.GET['game_id'])
    action = game.get_action(user)

    if action != Game.DISCARD:
        return HttpResponseBadRequest(f"Can't {Game.DISCARD}. Please {action}")

    card = request.GET['card']
    if card not in game.users_hand(user):
        return HttpResponseBadRequest(f"Invalid discard: {card} is not in your hand")

    game.discard_card(user, card)
    return JsonResponse(data=game.state_dict(user))
