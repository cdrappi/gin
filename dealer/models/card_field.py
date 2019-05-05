from django.db import models
from gin_utils import deck


class CardField(models.CharField):
    """ e.g. 'Ah', 'Kc', '4s', etc. """

    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, 'max_length': 2, 'choices': deck.card_choices}
        super().__init__(*args, **kwargs)
