import copy
import datetime
import random

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from gin_utils import deck, ricky

from dealer.utils.game_state import GinRickyGameState


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
            'created_at': self.created_at,
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
        }

    @staticmethod
    def get_game_series(user):
        """

        :param user: (User)
        :return: ({str: [dict]})
        """
        player_in_series = Q(player_1=user) | Q(player_2=user)
        recent_or_active = Q(created_at__gt=Game.now() - datetime.timedelta(days=7)) | Q(is_complete=False)
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
            created_at=Game.now(),
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

    def create_game_state(self):
        return GinRickyGameState(
            turns=self.turns,
            shuffles=self.shuffles,
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
            last_draw_from_discard=self.last_draw_from_discard
        )

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

        if from_discard:
            card_drawn = self.top_of_discard
            self.add_to_hand(user, card_drawn)
            self.discard = self.discard[:-1]
            self.public_hud[card_drawn] = (
                Game.HUD_PLAYER_1 if is_p1
                else Game.HUD_PLAYER_2
            )
        else:
            card_drawn = self.top_of_deck
            self.add_to_hand(user, self.top_of_deck)
            self.deck = self.deck[1:]
            if len(self.deck) == 0:
                # if there are no cards left in the deck,
                # shuffle up the discards
                new_deck = copy.deepcopy(self.discard)
                random.shuffle(new_deck)
                self.deck = new_deck
                self.discard = []
                self.shuffles += 1
                # Both players know each others hands
                # at this point, so we can just do this:
                self.public_hud = {
                    **{c: Game.HUD_PLAYER_1 for c in self.p1_hand},
                    **{c: Game.HUD_PLAYER_2 for c in self.p2_hand}
                }

        if is_p1:
            self.p1_draws = False
            self.p1_discards = True
        elif is_p2:
            self.p2_draws = False
            self.p2_discards = True

        self.turns += 1
        self.last_draw = card_drawn
        self.last_draw_from_discard = from_discard

        self.save()
        CardDrawn.objects.create(
            player=user,
            game=self,
            card=card_drawn,
            turn=self.turns,
            shuffle=self.shuffles,
            from_discard=from_discard
        )

    @staticmethod
    def now():
        return datetime.datetime.now(tz=datetime.timezone.utc)

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

        if self.is_player_1(user):
            self.p1_hand = [c for c in self.p1_hand if c != card]
            self.p1_discards = False
            self.p2_draws = True
            self.p1_last_completed_turn = self.now()
        elif self.is_player_2(user):
            self.p2_hand = [c for c in self.p2_hand if c != card]
            self.p2_discards = False
            self.p1_draws = True
            self.p2_last_completed_turn = self.now()

        # add discard to HUD
        if self.discard:
            self.public_hud[self.discard[-1]] = Game.HUD_DISCARD
        self.public_hud[card] = Game.HUD_TOP_OF_DECK

        self.discard.append(card)

        if self.user_points(user) == 0:
            self.is_complete = True
            self.is_active = False
            if self.is_player_1(user):
                self.p1_points = 0
                self.p2_points = self.user_points(self.player_2)
            else:
                self.p1_points = self.user_points(self.player_1)
                self.p2_points = 0

        self.turns += 1
        self.save()

        CardDiscarded.objects.create(
            player=user,
            game=self,
            card=card,
            turn=self.turns,
            shuffle=self.shuffles,
        )
        if self.is_complete:
            self.series.process_complete_game(self)

    def user_points(self, user):
        """

        :param user: (User)
        :return: (int)
        """
        users_hand = self.users_hand(user)
        return ricky.hand_points(users_hand)

    def get_action(self, user):
        """

        :param user: (User)
        :return: (str) 'draw', 'discard', 'wait'
        """
        if self.is_complete:
            return self.COMPLETE

        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)

        if (is_p1 and self.p1_draws) or (is_p2 and self.p2_draws):
            return self.DRAW
        elif (is_p1 and self.p1_discards) or (is_p2 and self.p2_discards):
            return self.DISCARD
        else:
            return self.WAIT

    def get_state(self, user):
        """

        :param user: (User)
        :return: (str, dict)
        """
        is_p1 = self.is_player_1(user)
        is_p2 = self.is_player_2(user)
        if not (is_p1 or is_p2):
            return {}

        opponent = self.get_opponent(user)
        common_items = {
            'series_id': self.series.id,
            'id': self.id,
            'opponent_id': opponent.id,
            'opponent_username': opponent.username
        }
        if self.is_complete:
            return {
                'points': self.p1_points if is_p1 else self.p2_points,
                'opponent_hand': self.opponents_hand(user),
                'opponent_points': self.p1_points if is_p2 else self.p2_points,
                'action': Game.COMPLETE,
                **common_items
            }

        final_info = {'action': self.get_action(user), 'last_draw': None}
        if final_info['action'] == "draw":
            final_info['last_draw'] = (
                self.last_draw
                if self.last_draw_from_discard
                else Game.DECK_DUMMY_CARD
            )
        if final_info['action'] == "discard":
            final_info['drawn_card'] = self.last_draw

        hand = ricky.sort_hand(self.users_hand(user))

        def transform_loc(loc):
            """
            :param loc: (str) one of {"1", "2", "t", "d"}
            :return: (str) one of {"u", "o", "d", "t"}
            """
            if loc == Game.HUD_PLAYER_1:
                return Game.HUD_USER if is_p1 else Game.HUD_OPPONENT
            elif loc == Game.HUD_PLAYER_2:
                return Game.HUD_USER if is_p2 else Game.HUD_OPPONENT
            else:
                return loc

        transformed_hud = {
            card: transform_loc(loc) for card, loc in self.public_hud.items()
        }
        return {
            'hand': hand,
            'points': ricky.hand_points(hand),
            'top_of_discard': self.top_of_discard,
            'deck_length': len(self.deck),
            'last_completed_turn': (
                self.p1_last_completed_turn if is_p1
                else self.p2_last_completed_turn
            ),
            'hud': {**transformed_hud, **{c: Game.HUD_USER for c in hand}},
            **common_items,
            **final_info
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

    @property
    def top_of_discard(self):
        if len(self.discard) == 0:
            return None
        return self.discard[-1]

    @property
    def top_of_deck(self):
        return self.deck[0]

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

    def opponents_hand(self, user):
        assert user in {self.player_1, self.player_2}
        opponent = self.player_1 if user == self.player_2 else self.player_2
        return self.users_hand(opponent)

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
            p1_last_completed_turn=Game.now(),
            p2_last_completed_turn=Game.now(),
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
