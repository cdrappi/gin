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
    top_card = CardField()

    p1_discards = models.BooleanField()
    p1_draws = models.BooleanField()
    p2_discards = models.BooleanField()
    p2_draws = models.BooleanField()


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
