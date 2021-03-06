# Generated by Django 2.2 on 2019-04-21 02:52

import dealer.models
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_over', models.BooleanField(default=False)),
                ('p1_wins', models.NullBooleanField()),
                ('shuffles', models.IntegerField(default=0)),
                ('deck', django.contrib.postgres.fields.ArrayField(base_field=dealer.models.CardField(choices=[('2h', '2 of h'), ('2d', '2 of d'), ('2c', '2 of c'), ('2s', '2 of s'), ('3h', '3 of h'), ('3d', '3 of d'), ('3c', '3 of c'), ('3s', '3 of s'), ('4h', '4 of h'), ('4d', '4 of d'), ('4c', '4 of c'), ('4s', '4 of s'), ('5h', '5 of h'), ('5d', '5 of d'), ('5c', '5 of c'), ('5s', '5 of s'), ('6h', '6 of h'), ('6d', '6 of d'), ('6c', '6 of c'), ('6s', '6 of s'), ('7h', '7 of h'), ('7d', '7 of d'), ('7c', '7 of c'), ('7s', '7 of s'), ('8h', '8 of h'), ('8d', '8 of d'), ('8c', '8 of c'), ('8s', '8 of s'), ('9h', '9 of h'), ('9d', '9 of d'), ('9c', '9 of c'), ('9s', '9 of s'), ('Th', 'T of h'), ('Td', 'T of d'), ('Tc', 'T of c'), ('Ts', 'T of s'), ('Jh', 'J of h'), ('Jd', 'J of d'), ('Jc', 'J of c'), ('Js', 'J of s'), ('Qh', 'Q of h'), ('Qd', 'Q of d'), ('Qc', 'Q of c'), ('Qs', 'Q of s'), ('Kh', 'K of h'), ('Kd', 'K of d'), ('Kc', 'K of c'), ('Ks', 'K of s'), ('Ah', 'A of h'), ('Ad', 'A of d'), ('Ac', 'A of c'), ('As', 'A of s')], max_length=2), size=None)),
                ('top_card', dealer.models.CardField(choices=[('2h', '2 of h'), ('2d', '2 of d'), ('2c', '2 of c'), ('2s', '2 of s'), ('3h', '3 of h'), ('3d', '3 of d'), ('3c', '3 of c'), ('3s', '3 of s'), ('4h', '4 of h'), ('4d', '4 of d'), ('4c', '4 of c'), ('4s', '4 of s'), ('5h', '5 of h'), ('5d', '5 of d'), ('5c', '5 of c'), ('5s', '5 of s'), ('6h', '6 of h'), ('6d', '6 of d'), ('6c', '6 of c'), ('6s', '6 of s'), ('7h', '7 of h'), ('7d', '7 of d'), ('7c', '7 of c'), ('7s', '7 of s'), ('8h', '8 of h'), ('8d', '8 of d'), ('8c', '8 of c'), ('8s', '8 of s'), ('9h', '9 of h'), ('9d', '9 of d'), ('9c', '9 of c'), ('9s', '9 of s'), ('Th', 'T of h'), ('Td', 'T of d'), ('Tc', 'T of c'), ('Ts', 'T of s'), ('Jh', 'J of h'), ('Jd', 'J of d'), ('Jc', 'J of c'), ('Js', 'J of s'), ('Qh', 'Q of h'), ('Qd', 'Q of d'), ('Qc', 'Q of c'), ('Qs', 'Q of s'), ('Kh', 'K of h'), ('Kd', 'K of d'), ('Kc', 'K of c'), ('Ks', 'K of s'), ('Ah', 'A of h'), ('Ad', 'A of d'), ('Ac', 'A of c'), ('As', 'A of s')], max_length=2)),
                ('player_1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='first_games', to=settings.AUTH_USER_MODEL)),
                ('player_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StartingHand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hand', django.contrib.postgres.fields.ArrayField(base_field=dealer.models.CardField(choices=[('2h', '2 of h'), ('2d', '2 of d'), ('2c', '2 of c'), ('2s', '2 of s'), ('3h', '3 of h'), ('3d', '3 of d'), ('3c', '3 of c'), ('3s', '3 of s'), ('4h', '4 of h'), ('4d', '4 of d'), ('4c', '4 of c'), ('4s', '4 of s'), ('5h', '5 of h'), ('5d', '5 of d'), ('5c', '5 of c'), ('5s', '5 of s'), ('6h', '6 of h'), ('6d', '6 of d'), ('6c', '6 of c'), ('6s', '6 of s'), ('7h', '7 of h'), ('7d', '7 of d'), ('7c', '7 of c'), ('7s', '7 of s'), ('8h', '8 of h'), ('8d', '8 of d'), ('8c', '8 of c'), ('8s', '8 of s'), ('9h', '9 of h'), ('9d', '9 of d'), ('9c', '9 of c'), ('9s', '9 of s'), ('Th', 'T of h'), ('Td', 'T of d'), ('Tc', 'T of c'), ('Ts', 'T of s'), ('Jh', 'J of h'), ('Jd', 'J of d'), ('Jc', 'J of c'), ('Js', 'J of s'), ('Qh', 'Q of h'), ('Qd', 'Q of d'), ('Qc', 'Q of c'), ('Qs', 'Q of s'), ('Kh', 'K of h'), ('Kd', 'K of d'), ('Kc', 'K of c'), ('Ks', 'K of s'), ('Ah', 'A of h'), ('Ad', 'A of d'), ('Ac', 'A of c'), ('As', 'A of s')], max_length=2), size=7)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dealer.Game')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardDrawn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', dealer.models.CardField(choices=[('2h', '2 of h'), ('2d', '2 of d'), ('2c', '2 of c'), ('2s', '2 of s'), ('3h', '3 of h'), ('3d', '3 of d'), ('3c', '3 of c'), ('3s', '3 of s'), ('4h', '4 of h'), ('4d', '4 of d'), ('4c', '4 of c'), ('4s', '4 of s'), ('5h', '5 of h'), ('5d', '5 of d'), ('5c', '5 of c'), ('5s', '5 of s'), ('6h', '6 of h'), ('6d', '6 of d'), ('6c', '6 of c'), ('6s', '6 of s'), ('7h', '7 of h'), ('7d', '7 of d'), ('7c', '7 of c'), ('7s', '7 of s'), ('8h', '8 of h'), ('8d', '8 of d'), ('8c', '8 of c'), ('8s', '8 of s'), ('9h', '9 of h'), ('9d', '9 of d'), ('9c', '9 of c'), ('9s', '9 of s'), ('Th', 'T of h'), ('Td', 'T of d'), ('Tc', 'T of c'), ('Ts', 'T of s'), ('Jh', 'J of h'), ('Jd', 'J of d'), ('Jc', 'J of c'), ('Js', 'J of s'), ('Qh', 'Q of h'), ('Qd', 'Q of d'), ('Qc', 'Q of c'), ('Qs', 'Q of s'), ('Kh', 'K of h'), ('Kd', 'K of d'), ('Kc', 'K of c'), ('Ks', 'K of s'), ('Ah', 'A of h'), ('Ad', 'A of d'), ('Ac', 'A of c'), ('As', 'A of s')], max_length=2)),
                ('turn', models.IntegerField()),
                ('shuffle', models.IntegerField()),
                ('from_discard', models.BooleanField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dealer.Game')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CardDiscarded',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', dealer.models.CardField(choices=[('2h', '2 of h'), ('2d', '2 of d'), ('2c', '2 of c'), ('2s', '2 of s'), ('3h', '3 of h'), ('3d', '3 of d'), ('3c', '3 of c'), ('3s', '3 of s'), ('4h', '4 of h'), ('4d', '4 of d'), ('4c', '4 of c'), ('4s', '4 of s'), ('5h', '5 of h'), ('5d', '5 of d'), ('5c', '5 of c'), ('5s', '5 of s'), ('6h', '6 of h'), ('6d', '6 of d'), ('6c', '6 of c'), ('6s', '6 of s'), ('7h', '7 of h'), ('7d', '7 of d'), ('7c', '7 of c'), ('7s', '7 of s'), ('8h', '8 of h'), ('8d', '8 of d'), ('8c', '8 of c'), ('8s', '8 of s'), ('9h', '9 of h'), ('9d', '9 of d'), ('9c', '9 of c'), ('9s', '9 of s'), ('Th', 'T of h'), ('Td', 'T of d'), ('Tc', 'T of c'), ('Ts', 'T of s'), ('Jh', 'J of h'), ('Jd', 'J of d'), ('Jc', 'J of c'), ('Js', 'J of s'), ('Qh', 'Q of h'), ('Qd', 'Q of d'), ('Qc', 'Q of c'), ('Qs', 'Q of s'), ('Kh', 'K of h'), ('Kd', 'K of d'), ('Kc', 'K of c'), ('Ks', 'K of s'), ('Ah', 'A of h'), ('Ad', 'A of d'), ('Ac', 'A of c'), ('As', 'A of s')], max_length=2)),
                ('turn', models.IntegerField()),
                ('shuffle', models.IntegerField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dealer.Game')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
