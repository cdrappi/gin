import datetime
import random
from typing import Dict, Tuple

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from gin_utils.ricky.game_state import GinRickyGameState
from gin_utils.ricky.utils import deal_new_game

from dealer.models.action_logging import CardDiscarded, CardDrawn, StartingHand
from dealer.models.card_field import CardField


class Game(models.Model):
    series = models.ForeignKey('dealer.GameSeries', on_delete=models.CASCADE, null=True)

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

    action_play = 'play'
    action_draw = GinRickyGameState.action_draw
    action_discard = GinRickyGameState.action_discard
    action_wait = GinRickyGameState.action_wait
    action_complete = GinRickyGameState.action_complete

    action_map = {
        action_draw: action_play,
        action_discard: action_play,
    }

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
        self.is_complete = game_state.is_complete

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
        dealt_game = deal_new_game()
        p1_goes_first = random.choice([True, False])

        game_state = GinRickyGameState(
            p1_draws=p1_goes_first,
            p1_discards=False,
            p2_draws=not p1_goes_first,
            p2_discards=False,
            **dealt_game
        )
        game = Game(
            series=game_series,
            p1_last_completed_turn=now(),
            p2_last_completed_turn=now(),
        )
        game.save_from_game_state(game_state)

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
            Game.action_play: [],
            GinRickyGameState.action_wait: [],
            GinRickyGameState.action_complete: [],
        }

        for game in games:
            game_state = game.get_state(user)
            action = game_state['action']
            mapped_action = Game.action_map.get(action, action)
            users_games[mapped_action].append(game_state)
        
        def _sort_games(gs: Dict) -> Tuple[int, datetime.datetime]:
            return (
                (
                    0
                    if gs['action'] == Game.action_discard
                    else 1
                ),
                gs['last_completed_turn']
            )

        users_games[Game.action_play].sort(key=_sort_games)
        return users_games
