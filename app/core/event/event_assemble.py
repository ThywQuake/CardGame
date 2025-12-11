from app.core.event.event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game


class DrawCardEvent(Event):
    pass


class PlayCardEvent(Event):
    pass


class EndTurnEvent(Event):
    pass


class StartTurnEvent(Event):
    pass


class SurprisePhaseEvent(Event):
    pass

    def execute(self, game: Game) -> Events:
        return []
