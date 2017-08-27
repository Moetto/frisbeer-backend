from django.contrib import admin
from frisbeer.models import *


class PlayerInGameInline(admin.TabularInline):
    model = GamePlayerRelation


class GameAdmin(admin.ModelAdmin):
    inlines = [PlayerInGameInline, ]


admin.site.register(Player)
admin.site.register(Game, GameAdmin)
admin.site.register(Location)
admin.site.register(Rank)
