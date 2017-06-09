from django.core.exceptions import ValidationError
from django.templatetags.static import static
from rest_framework import serializers

from frisbeer.models import Rank, Player, GamePlayerRelation, Game, Location


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ('name', 'image_url', 'numerical_value')
        read_only_fields = ["numerical_value", "name", "image_url"]

    def to_representation(self, instance):
        return {
            'numerical_value': instance.numerical_value,
            'name': instance.name,
            'image_url': static(instance.image_url)
        }


class PlayerSerializer(serializers.ModelSerializer):
    rank = RankSerializer(many=False, read_only=True, allow_null=True)

    class Meta:
        model = Player
        fields = ('id', 'name', 'score', 'rank')
        read_only_fields = ('score', 'rank', 'id')


class PlayersValidator:
    def __call__(self, values):
        players = values.get("players", None)
        if not players or len(players) != 6:
            raise ValidationError("Round requires exactly six players")


class PlayerInGameSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(source='player.id')
    name = serializers.ReadOnlyField(source='player.name', required=False)
    team = serializers.IntegerField(required=False)
    rank = RankSerializer(source='player.rank', required=False, allow_null=True)

    class Meta:
        model = GamePlayerRelation
        fields = ('id', 'name', 'team', 'rank')


class GameSerializer(serializers.ModelSerializer):
    players = PlayerInGameSerializer(many=True, source='gameplayerrelation_set', partial=True)

    class Meta:
        model = Game
        fields = "__all__"

    def update(self, instance, validated_data):
        try:
            players = validated_data.pop('gameplayerrelation_set')
        except KeyError:
            players = None
        s = super().update(instance, validated_data)
        if players:
            GamePlayerRelation.objects.filter(game=s).delete()
            for player in players:
                p = Player.objects.get(id=player["player"]["id"])
                try:
                    team = player["team"]
                except KeyError:
                    team = 0
                g, created = GamePlayerRelation.objects.get_or_create(game=s, player=p)
                g.team = team
                g.save()
        return s

    def create(self, validated_data):
        players = validated_data.pop('gameplayerrelation_set')
        s = super().create(validated_data)
        if players:
            GamePlayerRelation.objects.filter(game=s).delete()
            for player in players:
                p = Player.objects.get(id=player["player"]["id"])
                team = player["team"] if player["team"] else 0
                g, created = GamePlayerRelation.objects.get_or_create(game=s, player=p)
                g.team = team
                g.save()
        return s


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

    def validate(self, attrs):
        su = super().validate(attrs)
        try:
            longitude = su.get("longitude", self.instance.longitude)
        except AttributeError:
            longitude = None

        try:
            latitude = su.get("latitude", self.instance.latitude)
        except AttributeError:
            latitude = None

        if latitude is not None and (latitude > 90 or latitude < -90):
            raise ValidationError("Latitude must be between -90 and 90")
        if longitude is not None and (longitude > 180 or longitude < -180):
            raise ValidationError("Longitude must be between -180 and 180")
        if (longitude is None and latitude is not None) or (longitude is not None and latitude is None):
            raise ValidationError(
                "If longitude is provided then latitude is required and vice versa. Both can be null.")

        return su