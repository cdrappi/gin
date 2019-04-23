from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponseBadRequest
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from dealer.models import Game
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
        other_users = User.objects.exclude(id=request.user.id)
        serializer = UserSerializer(other_users, many=True)
        return Response(serializer.data)


def create_game(request):
    """

    :param request:
    :return:
    """
    user = request.user
    game = Game.new_game(user.id, request.POST['opponent_id'])
    return JsonResponse(data=game.get_state(user))


def get_users_games(request):
    """

    :param request:
    :return:
    """
    print(dir(request))
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

    return JsonResponse(data=game.get_state(user))


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
    return JsonResponse(data=game.get_state(user))
