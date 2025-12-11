from typing import TYPE_CHECKING
import random
from app.core.event.event_assemble import SurprisePhaseEvent

if TYPE_CHECKING:
    from app.core import Events, Game


class SuperBlock:
    def __init__(self, **kwargs):
        self.max_block: int = kwargs.get("max_block", 8)
        self.current_block: int = kwargs.get("current_block", 0)
        self.endurance: int = kwargs.get("endurance", 3)

    def defend(self, game: Game) -> Events:
        if self.endurance <= 0:
            return []
        random_block = random.randint(1, 3)
        self.current_block = min(self.max_block, self.current_block + random_block)
        if self.current_block == self.max_block:
            self.endurance -= 1
            self.current_block = 0
            return [SurprisePhaseEvent(game=game)]
        return []
