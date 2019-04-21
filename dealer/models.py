from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models

ranks = list('23456789TJQKA')
suits = set('cdhs')

CARD_CHOICES = [(f'{rank}{suit}', f'{rank} of {suit}')
                for rank in ranks for suit in suits]


class CardField(models.CharField):
    """ e.g. 'Ah', 'Kc', '4s', etc. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, max_length=2, choices=CARD_CHOICES)


class Game(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.SET_NULL)
    player_2 = models.ForeignKey(User, on_delete=models.SET_NULL)

    is_over = models.BooleanField(default=False)
    p1_wins = models.NullBooleanField()

    shuffles = models.IntegerField(default=0)

    # denormalize for convenience... only edit the Game model during the game,
    # and write-only to all other models.
    deck = ArrayField(base_field=CardField())
    top_card = CardField()


class StartingHand(models.Model):
    player = models.ForeignKey(User, on_delete=models.SET_NULL)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    hand = ArrayField(base_field=CardField(), size=7)


class CardAction(models.Model):
    player = models.ForeignKey(User, on_delete=models.SET_NULL)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    card = models.CharField()
    turn = models.IntegerField()
    shuffle = models.IntegerField()

    class Meta:
        abstract = True


class CardDrawn(CardAction):
    from_discard = models.BooleanField()


class CardDiscarded(CardAction):
    pass
