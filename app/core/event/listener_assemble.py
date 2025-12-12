from app.core.engine.game import Game
from app.core.event.event import Event, Events
from app.core.event.listener import Listener
from app.core.base import Lifetime, Position
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game
    from app.core.event.event import Event


class GameOverListener(Listener):
    def __init__(self, **kwargs):
        from app.core.event.event_assemble import HeroDieEvent

        super().__init__(**kwargs)

        self.on_events = [HeroDieEvent]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core.engine.exception import GameOverException
        from app.core.event.event_assemble import HeroDieEvent
        from app.core.entity.player import Player

        if isinstance(event.source, Player) and isinstance(event, HeroDieEvent):
            raise GameOverException(winner=event.source.opposite_faction())

        return []


class SurprisePhaseListener(Listener):
    def __init__(self, **kwargs):
        from app.core.event.event_assemble import HeroTakeDamageEvent, HeroHurtEvent

        super().__init__(**kwargs)

        self.on_events = [HeroTakeDamageEvent, HeroHurtEvent]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core.event.event_assemble import HeroTakeDamageEvent, HeroHurtEvent

        if game.surprise_phase and isinstance(
            event, (HeroTakeDamageEvent, HeroHurtEvent)
        ):
            event.cancel()
        return []
