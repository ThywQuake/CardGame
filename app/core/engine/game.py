from app.core.entity import Player, Field
from app.core.event import EventManager
from app.core.base import Faction
from app.core.event import Event


class Game:
    def __init__(self, **kwargs):
        self.zombie_player: Player = kwargs.get(
            "zombie_player", Player(faction=Faction.ZOMBIE)
        )
        self.plant_player: Player = kwargs.get(
            "plant_player", Player(faction=Faction.PLANT)
        )
        self.current_player: Player = self.zombie_player

        self.event_manager = EventManager(game=self)

        self.field = Field()

    def step(self, event: Event):
        """Process a game step based on the provided action."""
        # Implementation of game step processing goes here
        pass
