from django.contrib.postgres.fields import ArrayField
from django.db import models

from dealer.models.card_field import CardField


class StartingHand(models.Model):
    player = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    game = models.ForeignKey('dealer.Game', on_delete=models.CASCADE)
    hand = ArrayField(base_field=CardField(), size=7)


class CardAction(models.Model):
    player = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    game = models.ForeignKey('dealer.Game', on_delete=models.CASCADE)
    card = CardField()
    turn = models.IntegerField()
    shuffle = models.IntegerField()

    class Meta:
        abstract = True


class CardDrawn(CardAction):
    from_discard = models.BooleanField()


class CardDiscarded(CardAction):
    pass
