from django.http.response import JsonResponse
from dealer.models import Game

# Create your views here.

def create_game(request):
    player_1_id = request.POST['player_1_id']
    player_2_id = request.POST['player_2_id']
    game = Game.objects.create(player_1_id, player_2_id)
    return JsonResponse

