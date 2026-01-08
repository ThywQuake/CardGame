from app.core.event.event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game


class EndPhaseEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: "Game") -> Events:
        # Implementation of end phase logic goes here
        ...
