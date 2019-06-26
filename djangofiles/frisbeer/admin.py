from django.contrib import admin
from frisbeer.models import *


class PlayerInGameInline(admin.TabularInline):
    model = GamePlayerRelation


class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInGameInline, ]

    def get_changeform_initial_data(self, request):
        return {'season': Season.current().id }


class PlayerInTeamInline(admin.TabularInline):
    model = TeamPlayerRelation


class TeamAdmin(admin.ModelAdmin):
    inlines = [PlayerInTeamInline]


admin.site.register(Player)
admin.site.register(Game, GameAdmin)
admin.site.register(Location)
admin.site.register(Rank)
admin.site.register(Season)
admin.site.register(Team, TeamAdmin)
