import copy
import itertools
import random

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q

ranks = list('23456789TJQKA')
suits = set('cdhs')

CARD_CHOICES = [(f'{rank}{suit}', f'{rank} of {suit}')
                for rank in ranks for suit in suits]

CARD_VALUES = {
    'A': 1,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    **{d: int(d) for d in '23456789'}
}


class CardField(models.CharField):
    """ e.g. 'Ah', 'Kc', '4s', etc. """

    def __init__(self, *args, **kwargs):
        kwargs = {**kwargs, 'max_length': 2, 'choices': CARD_CHOICES}
        super().__init__(*args, **kwargs)


class Game(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='first_games')
    player_2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='second_games')

    is_complete = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    p1_points = models.IntegerField(null=True)
    p2_points = models.IntegerField(null=True)

    shuffles = models.IntegerField(default=0)

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

    PLAY = 'play'
    DRAW = 'draw'
    DISCARD = 'discard'
    WAIT = 'wait'
    COMPLETE = 'complete'

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
            self.add_to_hand(user, self.top_of_discard)
            self.discard = self.discard[:-1]
        else:
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

        if is_p1:
            self.p1_draws = False
            self.p1_discards = True
        elif is_p2:
            self.p2_draws = False
            self.p2_discards = True
        self.save()

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
        elif self.is_player_2(user):
            self.p2_hand = [c for c in self.p2_hand if c != card]
            self.p2_discards = False
            self.p1_draws = True

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

        self.save()

    def user_points(self, user):
        """

        :param user: (User)
        :return: (int)
        """
        users_hand = self.users_hand(user)
        return self.hand_points(users_hand)

    @staticmethod
    def yield_hand_combos(hand):
        for combo_3 in itertools.combinations(hand, 3):
            combo_4 = [c for c in hand if c not in combo_3]
            yield combo_3, combo_4

    @classmethod
    def combos_points(cls, combo_3, combo_4):
        return cls.combo_points(combo_3) + cls.combo_points(combo_4)

    @classmethod
    def hand_points(cls, hand):
        """

        :param hand: ([str]) list of cards
        :return: (int)
        """
        points = 14 * 7
        for combo_3, combo_4 in cls.yield_hand_combos(hand):
            combo_points = cls.combos_points(combo_3, combo_4)
            if combo_points == 0:
                return 0
            points = min(combo_points, points)

        return points

    @staticmethod
    def sort_cards(cards):
        return sorted(cards, key=lambda c: CARD_VALUES[c[0]])

    def sorted_hand(self, hand):
        """
        :param hand: ([str])
        :return: ([str])
        """
        combo_3, combo_4 = min(self.yield_hand_combos(hand), key=lambda k: self.combos_points(k[0], k[1]))
        sorted_hand = self.sort_cards(combo_3) + self.sort_cards(combo_4)
        rank_points = self.calculate_points([c[0] for c in sorted_hand])
        combo_points = self.combos_points(combo_3, combo_4)
        if rank_points == combo_points:
            return self.sort_cards(sorted_hand)
        else:
            return sorted_hand

    @classmethod
    def combo_points(cls, card_combo):
        """

        :param card_combo: ([str])
        :return: (int)
        """
        first_rank, first_suit = card_combo[0]
        card_ranks = [card[0] for card in card_combo]

        if all(r == first_rank for r in card_ranks):
            # all cards are same rank
            return 0

        if any(card[1] != first_suit for card in card_combo):
            # cards are not of same rank and not of same suit,
            # so return the points
            return cls.calculate_points(card_ranks)

        # NOTE: if we get to this point, cards have same suit
        # so we just need to check if they make a valid 3- or 4-straight

        # handle fact that aces can be 1 or 14
        values_ace_as_1 = sorted(CARD_VALUES[r] for r in card_ranks)
        rank_combos = [values_ace_as_1]
        if any(r == 'A' for r in card_ranks):
            rank_combos.append(sorted(14 if value == 1 else value for value in values_ace_as_1))

        for rank_combo in rank_combos:
            if cls.ranks_make_a_straight(rank_combo):
                return 0

        return cls.calculate_points(card_ranks)

    @staticmethod
    def calculate_points(card_ranks):
        return sum(CARD_VALUES[r] for r in card_ranks)

    @staticmethod
    def ranks_make_a_straight(rank_combo):
        """

        :param rank_combo: ([int])
        :return: (bool)
        """
        for r1, r2 in zip(rank_combo[:-1], rank_combo[1:]):
            if r1 != r2 - 1:
                return False
        return True

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

        final_info = {'action': self.get_action(user)}
        if self.is_complete:
            final_info = {
                'points': self.p1_points if is_p1 else self.p2_points,
                'opponent_hand': self.opponents_hand(user),
                'opponent_points': self.p1_points if is_p2 else self.p2_points,
                'action': Game.COMPLETE,
            }

        return {
            'id': self.id,
            'opponent_id': opponent.id,
            'opponent_username': opponent.username,
            'hand': self.sorted_hand(self.users_hand(user)),
            'top_of_discard': self.top_of_discard,
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
            'discard': [deck[14]],
            'deck': deck[15:],
        }

    @staticmethod
    def new_game(player_1_id, player_2_id):
        """

        :param player_1_id: (int)
        :param player_2_id: (int)
        :return:
        """
        dealt_game = Game.deal_new_game()
        game = Game(
            player_1_id=player_1_id,
            player_2_id=player_2_id,
            is_complete=False,
            p1_points=None,
            p2_points=None,
            shuffles=0,
            p1_draws=True,
            p1_discards=False,
            p2_draws=False,
            p2_discards=False,
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
        player_in_game = Q(player_1=user) | Q(player_2=user)
        games = Game.objects.filter(player_in_game).order_by('id')  # .filter(is_active=True)
        users_games = {
            Game.PLAY: [],
            Game.WAIT: [],
            Game.COMPLETE: [],
        }
        for game in games:
            game_state = game.get_state(user)
            if game_state['action'] in {'draw', 'discard'}:
                users_games['play'].append(game_state)
            else:
                users_games[game_state['action']].append(game_state)

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
