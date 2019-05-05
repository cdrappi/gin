import json

from django.contrib.auth.models import User
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from dealer.models import Game, GameSeries
from dealer.serializers import UserSerializer, UserSerializerWithToken


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            other_users = User.objects.exclude(id=request.user.id)
            serializer = UserSerializer(other_users, many=True)
            return Response(serializer.data)
        except:
            return Response([])


@csrf_exempt
def create_game_series(request):
    """

    :param request:
    :return:
    """
    posted_data = json.loads(request.body)
    user = request.user
    game_series = GameSeries.new_game_series(
        player_1_id=user.id,
        player_2_id=posted_data['opponent_id'],
        points_to_stop=posted_data.get('points_to_stop', 0),
        concurrent_games=posted_data.get('concurrent_games', 1),
        cents_per_point=posted_data.get('cents_per_point', 0),
    )
    return JsonResponse(data={'id': game_series.id})


def get_users_games(request):
    """

    :param request:
    :return:
    """
    if True:
        users_games = Game.list_users_games(request.user)
        return JsonResponse(data=users_games)
    # TODO: make more specific
    # except:
    #     return JsonResponse(data={
    #         Game.PLAY: [],
    #         Game.WAIT: [],
    #         Game.COMPLETE: [],
    #     })


def get_users_game_series(request):
    """

    :param request:
    :return:
    """
    try:
        users_series = GameSeries.get_game_series(request.user)
        return JsonResponse(data=users_series)
    except:
        return JsonResponse(
            data={GameSeries.COMPLETE: [], GameSeries.INCOMPLETE: []}
        )


@csrf_exempt  # TODO: add CSRF token to React fetch headers
def draw_card(request):
    """

    :param request:
    :return:
    """
    user = request.user
    posted_data = json.loads(request.body)
    game = Game.objects.get(id=posted_data['game_id'])
    action = game.get_action(user)
    if action != Game.DRAW:
        return HttpResponseBadRequest(f"Can't {Game.DRAW}. Please {action}")

    if posted_data['from_discard']:
        game.draw_from_discard(user)
    else:
        game.draw_from_deck(user)

    return JsonResponse(data=game.get_state(user))


@csrf_exempt  # TODO: add CSRF token to React fetch headers
def discard_card(request):
    """

    :param request:
    :return:
    """
    user = request.user
    posted_data = json.loads(request.body)
    game = Game.objects.get(id=posted_data['game_id'])
    action = game.get_action(user)

    if action != Game.DISCARD:
        return HttpResponseBadRequest(f"Can't {Game.DISCARD}. Please {action}")

    card = posted_data['card']
    if card not in game.users_hand(user):
        return HttpResponseBadRequest(f"Invalid discard: {card} is not in your hand")

    game.discard_card(user, card)
    return JsonResponse(data=game.get_state(user))
