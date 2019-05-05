import datetime
import random

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from gin_utils import deck, ricky

from dealer.utils.gin_ricky_game_state import GinRickyGameState


class CardField(models.CharField):
    """ e.g. 'Ah', 'Kc', '4s', etc. """

    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, 'max_length': 2, 'choices': deck.card_choices}
        super().__init__(*args, **kwargs)


class GameSeries(models.Model):
    """ hold a collection of games defined by some method to stop """
    player_1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='first_series')
    player_2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='second_series')

    is_complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_created=True)
    completed_at = models.DateTimeField(null=True)

    points_to_stop = models.IntegerField(default=0)
    concurrent_games = models.IntegerField(default=1)
    cents_per_point = models.IntegerField(default=0)

    p1_points = models.IntegerField(default=0)
    p2_points = models.IntegerField(default=0)

    COMPLETE = 'complete'
    INCOMPLETE = 'incomplete'

    def __str__(self):
        completed_games = self.game_set.filter(is_complete=True).count()
        return f'{self.player_1} vs. {self.player_2} ({self.p1_points}-{self.p2_points} / {completed_games})'

    def to_dict(self, user):
        assert user in {self.player_1, self.player_2}
        is_p1 = user == self.player_1
        opponent = self.player_2 if is_p1 else self.player_1

        return {
            'id': self.id,
            'user_id': user.id,
            'opponent_id': opponent.id,
            'opponent_username': opponent.username,
            'points': self.p1_points if is_p1 else self.p2_points,
            'opponent_points': self.p2_points if is_p1 else self.p1_points,
            'points_to_stop': self.points_to_stop,
            'complete_games': self.game_set.filter(is_complete=True).count(),
            'incomplete_games': self.game_set.filter(is_complete=False).count(),
            'concurrent_games': self.concurrent_games,
            'cents_per_point': self.cents_per_point,
            'is_complete': self.is_complete,
            'completed_at': self.completed_at,
            'created_at': self.created_at,
        }

    @staticmethod
    def get_game_series(user):
        """

        :param user: (User)
        :return: ({str: [dict]})
        """
        player_in_series = Q(player_1=user) | Q(player_2=user)
        recent_or_active = Q(completed_at__gt=now() - datetime.timedelta(days=7)) | Q(is_complete=False)
        series = (GameSeries
                  .objects
                  .filter(player_in_series)
                  .filter(recent_or_active)
                  .order_by('-id'))

        series_list = [gs.to_dict(user) for gs in series]
        return {
            GameSeries.COMPLETE: [s for s in series_list if s['is_complete']],
            GameSeries.INCOMPLETE: [s for s in series_list if not s['is_complete']]
        }

    @staticmethod
    def new_game_series(player_1_id, player_2_id, points_to_stop, concurrent_games, cents_per_point):
        """

        :param player_1_id:
        :param player_2_id:
        :param points_to_stop:
        :param concurrent_games:
        :param cents_per_point:
        :return:
        """
        game_series = GameSeries.objects.create(
            player_1_id=player_1_id,
            player_2_id=player_2_id,
            created_at=now(),
            completed_at=None,
            points_to_stop=points_to_stop,
            concurrent_games=concurrent_games,
            cents_per_point=cents_per_point,
        )
        for _ in range(concurrent_games):
            Game.new_game(game_series)
        return game_series

    def process_complete_game(self, game):
        """

        :param game: (Game)
        :return: None
        """
        self.p1_points += game.p1_points
        self.p2_points += game.p2_points

        incomplete_games = self.game_set.filter(is_complete=False).count()

        if self.p1_points < self.points_to_stop and self.p2_points < self.points_to_stop:
            if incomplete_games < self.concurrent_games:
                Game.new_game(game_series=self)

        if incomplete_games == 0:
            self.is_complete = True
            self.completed_at = now()

        self.save()

    def refresh_score(self):
        """ recompute score for all games in series """

        self.p1_points = 0
        self.p2_points = 0

        games = self.game_set.filter(is_complete=True)
        for p1_pts, p2_pts in games.values_list('p1_points', 'p2_points'):
            self.p1_points += p1_pts
            self.p2_points += p2_pts

        self.save()


class Game(models.Model):
    series = models.ForeignKey(GameSeries, on_delete=models.CASCADE, null=True)

    is_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    p1_points = models.IntegerField(null=True)
    p2_points = models.IntegerField(null=True)

    turns = models.IntegerField(default=0)
    shuffles = models.IntegerField(default=0)

    # Map from card --> location
    public_hud = JSONField(default=dict)

    # denormalize for convenience... only edit the Game model during the game,
    # and write-only to all other models.
    deck = ArrayField(base_field=CardField())
    discard = ArrayField(base_field=CardField())
    p1_hand = ArrayField(base_field=CardField())
    p2_hand = ArrayField(base_field=CardField())

    p1_discards = models.BooleanField()
    p1_draws = models.BooleanField()
    p2_discards = models.BooleanField()
    p2_draws = models.BooleanField()

    p1_last_completed_turn = models.DateTimeField(null=False)
    p2_last_completed_turn = models.DateTimeField(null=False)

    # If player drew from discard, it is that card
    # If player drew from deck, it is None
    last_draw = CardField(null=True)
    last_draw_from_discard = models.NullBooleanField()

    PLAY = 'play'
    DRAW = 'draw'
    DISCARD = 'discard'
    WAIT = 'wait'
    COMPLETE = 'complete'

    HUD_PLAYER_1 = "1"
    HUD_PLAYER_2 = "2"
    HUD_TOP_OF_DECK = "t"
    HUD_DISCARD = "d"
    HUD_USER = "u"
    HUD_OPPONENT = "o"

    DECK_DUMMY_CARD = "?y"

    def build_game_state(self):
        """

        :return: (GinRickyGameState)
        """
        return GinRickyGameState(
            public_hud=self.public_hud,
            deck=self.deck,
            discard=self.discard,
            p1_hand=self.p1_hand,
            p2_hand=self.p2_hand,
            p1_discards=self.p1_discards,
            p1_draws=self.p1_draws,
            p2_discards=self.p2_discards,
            p2_draws=self.p2_draws,
            last_draw=self.last_draw,
            last_draw_from_discard=self.last_draw_from_discard,
            is_complete=self.is_complete,
            turns=self.turns,
            shuffles=self.shuffles,
            p1_points=self.p1_points,
            p2_points=self.p2_points
        )

    def save_from_game_state(self, game_state):
        """
        :param game_state:
        :return:
        """
        self.public_hud = game_state.public_hud
        self.deck = game_state.deck
        self.discard = game_state.discard

        self.p1_hand = game_state.p1_hand
        self.p2_hand = game_state.p2_hand

        self.p1_discards = game_state.p1_discards
        self.p1_draws = game_state.p1_draws
        self.p2_discards = game_state.p2_discards
        self.p2_draws = game_state.p2_draws

        self.last_draw = game_state.last_draw
        self.last_draw_from_discard = game_state.last_draw_from_discard

        self.turns = game_state.turns
        self.shuffles = game_state.shuffles

        self.p1_points = game_state.p1_points
        self.p2_points = game_state.p2_points

        self.save()

    @property
    def player_1(self):
        return self.series.player_1

    @property
    def player_2(self):
        return self.series.player_2

    def __str__(self):
        return f'Game(#{self.id}): {self.player_1} vs. {self.player_2}'

    def is_player_1(self, user):
        return user == self.player_1

    def is_player_2(self, user):
        return user == self.player_2

    def add_to_hand(self, user, card):
        if self.is_player_1(user):
            assert len(self.p1_hand) == 7
            self.p1_hand.append(card)
        elif self.is_player_2(user):
            assert len(self.p2_hand) == 7
            self.p2_hand.append(card)

    def draw_card(self, user, from_discard):
        """

        :param user:
        :param from_discard:
        :return:
        """
        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)

        assert (is_p1 and self.p1_draws) or (is_p2 and self.p2_draws)

        game_state = self.build_game_state()
        card_drawn = game_state.draw_card(from_discard)

        self.save_from_game_state(game_state)

        CardDrawn.objects.create(
            player=user,
            game=self,
            card=card_drawn,
            turn=self.turns,
            shuffle=self.shuffles,
            from_discard=from_discard
        )

    def draw_from_deck(self, user):
        self.draw_card(user, from_discard=False)

    def draw_from_discard(self, user):
        """

        :param user:
        :return: None
        """
        self.draw_card(user, from_discard=True)

    def discard_card(self, user, card):
        """

        :param user:
        :param card:
        :return: None
        """
        assert card in self.users_hand(user)

        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)

        assert (is_p1 and self.p1_discards) or (is_p2 and self.p2_discards)

        game_state = self.build_game_state()
        game_state.discard_card(card)

        if is_p1:
            self.p1_last_completed_turn = now()
        elif is_p2:
            self.p2_last_completed_turn = now()

        if game_state.is_complete:
            self.is_active = False
        self.save_from_game_state(game_state)

        CardDiscarded.objects.create(
            player=user,
            game=self,
            card=card,
            turn=self.turns,
            shuffle=self.shuffles,
        )
        if self.is_complete:
            self.series.process_complete_game(self)

    def get_action(self, user):
        """

        :param user: (User)
        :return: (str) 'draw', 'discard', 'wait'
        """
        is_p1 = self.is_player_1(user)
        game_state = self.build_game_state()
        return game_state.get_action(is_p1)

    def get_state(self, user):
        """

        :param user: (User)
        :return: (str, dict)
        """
        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)
        if not (is_p1 or is_p2):
            return {}

        game_state = self.build_game_state()

        opponent = self.get_opponent(user)
        return {
            'series_id': self.series.id,
            'id': self.id,
            'opponent_id': opponent.id,
            'opponent_username': opponent.username,
            'last_completed_turn': (
                self.p1_last_completed_turn if is_p1
                else self.p2_last_completed_turn
            ),
            **game_state.to_dict(is_p1),
        }

    def get_opponent(self, user):
        """

        :param user: (User)
        :return: (User)
        """
        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)

        if is_p1:
            return self.player_2
        elif is_p2:
            return self.player_1
        else:
            raise Exception(f"{user} is neither player 1 or player 2 in {self}")

    def users_hand(self, user):
        """

        :param user:
        :return:
        """
        if self.is_player_1(user):
            return self.p1_hand
        elif self.is_player_2(user):
            return self.p2_hand
        else:
            raise Exception(f"{user} is not in {self}")

    @staticmethod
    def new_game(game_series):
        """

        :param game_series: (GameSeries)
        :return:
        """
        dealt_game = ricky.deal_new_game()
        p1_goes_first = random.choice([True, False])
        game = Game(
            series=game_series,
            is_complete=False,
            p1_points=None,
            p2_points=None,
            shuffles=0,
            last_draw=None,
            p1_draws=p1_goes_first,
            p1_discards=False,
            p2_draws=not p1_goes_first,
            p2_discards=False,
            p1_last_completed_turn=now(),
            p2_last_completed_turn=now(),
            public_hud={dealt_game['discard'][0]: Game.HUD_TOP_OF_DECK},
            **dealt_game
        )
        game.save()
        StartingHand.objects.create(
            game=game,
            player=game.player_1,
            hand=game.p1_hand
        )
        StartingHand.objects.create(
            game=game,
            player=game.player_2,
            hand=game.p2_hand
        )
        return game

    @staticmethod
    def list_users_games(user):
        """

        :param user:
        :return:
        """
        player_in_game = Q(series__player_1=user) | Q(series__player_2=user)
        games = Game.objects.filter(player_in_game).order_by('id').filter(is_active=True)
        users_games = {
            Game.PLAY: [],
            Game.WAIT: [],
            Game.COMPLETE: [],
        }
        for game in games:
            game_state = game.get_state(user)
            if game_state['action'] in {'draw', 'discard'}:
                users_games[Game.PLAY].append(game_state)
            else:
                users_games[game_state['action']].append(game_state)

        users_games[Game.PLAY].sort(key=lambda k: k['last_completed_turn'])
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
