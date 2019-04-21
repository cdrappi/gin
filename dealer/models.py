import random

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q

ranks = list('23456789TJQKA')
suits = set('cdhs')

CARD_CHOICES = [(f'{rank}{suit}', f'{rank} of {suit}')
                for rank in ranks for suit in suits]


class CardField(models.CharField):
    """ e.g. 'Ah', 'Kc', '4s', etc. """

    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, 'max_length': 2, 'choices': CARD_CHOICES}
        super().__init__(*args, **kwargs)


class Game(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='first_games')
    player_2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='second_games')

    is_over = models.BooleanField(default=False)
    p1_wins = models.NullBooleanField()

    shuffles = models.IntegerField(default=0)

    # denormalize for convenience... only edit the Game model during the game,
    # and write-only to all other models.
    deck = ArrayField(base_field=CardField())
    discard = ArrayField(base_field=CardField())
    top_card = CardField()
    p1_hand = ArrayField(base_field=CardField())
    p2_hand = ArrayField(base_field=CardField())

    p1_discards = models.BooleanField()
    p1_draws = models.BooleanField()
    p2_discards = models.BooleanField()
    p2_draws = models.BooleanField()

    @staticmethod
    def random_deck():
        deck = [card for card, _ in CARD_CHOICES]
        random.shuffle(deck)
        return deck

    @staticmethod
    def deal_new_game():
        deck = Game.random_deck()
        return {
            'p1_hand': deck[0:7],
            'p2_hand': deck[7:14],
            'top_card': deck[14],
            'deck': deck[15:],
            'discard': []
        }

    @staticmethod
    def new_game(player_1_id, player_2_id):
        """

        :param player_1:
        :param player_2:
        :return:
        """
        dealt_game = Game.deal_new_game()
        game = Game(
            player_1_id=player_1_id,
            player_2_id=player_2_id,
            is_over=False,
            p1_wins=None,
            shuffles=0,
            p1_draws=True,
            p1_discards=False,
            p2_draws=False,
            p2_discards=False,
            **dealt_game
        )
        game.save()
        return game

    def get_action(self, user):
        """

        :param user: (User)
        :return: (str) 'draw', 'discard', 'wait'
        """
        is_p1 = user == self.player_1
        is_p2 = not is_p1

        if (is_p1 and self.p1_draws) or (is_p2 and self.p2_draws):
            return 'draw'
        elif (is_p1 and self.p1_discards) or (is_p2 and self.p2_discards):
            return 'discard'
        else:
            return 'wait'

    def parse_game(self, user):
        """

        :param user:
        :return: (str, dict)
        """
        is_p1 = user == self.player_1
        game_dict = {
            'id': self.id,
            'hand': self.p1_hand if is_p1 else self.p2_hand,
            'top_card': self.top_card,
        }
        return self.get_action(user), game_dict

    @staticmethod
    def list_users_games(user):
        """

        :param user:
        :return:
        """
        games = Game.objects.filter(Q(player_1=user) | Q(player_2=user))
        users_games = {
            'draw': [],
            'discard': [],
            'wait': [],
        }
        for game in games:
            action, parsed_game = game.parse_game(user)
            users_games[action].append(parsed_game)

        return users_games


class StartingHand(models.Model):
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    hand = ArrayField(base_field=CardField(), size=7)


class CardAction(models.Model):
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = CardField()
    turn = models.IntegerField()
    shuffle = models.IntegerField()

    class Meta:
        abstract = True


class CardDrawn(CardAction):
    from_discard = models.BooleanField()


class CardDiscarded(CardAction):
    pass
