from app.core.entity import Player, Field
from app.core.event import EventManager


class Game:
    def __init__(self, **kwargs):
        self.zombie_player: Player = kwargs.get("zombie_player", Player())
        self.plant_player: Player = kwargs.get("plant_player", Player())
        self.current_player: Player = self.zombie_player

        self.event_manager = EventManager(game=self)

        self.field = Field()
