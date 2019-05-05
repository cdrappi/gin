import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from dealer.models.game import Game


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
