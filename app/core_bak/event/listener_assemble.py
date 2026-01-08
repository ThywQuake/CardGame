from app.core_bak.engine.game import Game
from app.core_bak.event.event import Event, Events
from app.core_bak.event.listener import Listener
from app.core_bak.base import Lifetime, Position
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core_bak import Events
    from app.core_bak.engine.game import Game
    from app.core_bak.event.event import Event


class GameOverListener(Listener):
    def __init__(self, **kwargs):
        from app.core_bak.event.event_assemble import HeroDieEvent

        super().__init__(**kwargs)

        self.on_events = [HeroDieEvent]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core_bak.engine.exception import GameOverException
        from app.core_bak.event.event_assemble import HeroDieEvent
        from app.core_bak.entity.player import Player

        if isinstance(event.source, Player) and isinstance(event, HeroDieEvent):
            raise GameOverException(winner=event.source.opposite_faction())

        return []


class SurprisePhaseListener(Listener):
    def __init__(self, **kwargs):
        from app.core_bak.event.event_assemble import HeroTakeDamageEvent, HeroHurtEvent

        super().__init__(**kwargs)

        self.on_events = [HeroTakeDamageEvent, HeroHurtEvent]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core_bak.event.event_assemble import HeroTakeDamageEvent, HeroHurtEvent

        if game.surprise_phase and isinstance(
            event, (HeroTakeDamageEvent, HeroHurtEvent)
        ):
            event.cancel()
        return []


class HandActivateListener(Listener):
    def __init__(self, **kwargs):
        from app.core_bak.event.event_assemble import (
            ZombiePhaseStartEvent,
            PlantPhaseStartEvent,
            ZombieTrickPhaseStartEvent,
            CombatPhaseStartEvent,
        )

        super().__init__(**kwargs)

        self.on_events = [
            PlantPhaseStartEvent,
            ZombiePhaseStartEvent,
            ZombieTrickPhaseStartEvent,
            CombatPhaseStartEvent,
        ]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core_bak.event.event_assemble import (
            ZombiePhaseStartEvent,
            PlantPhaseStartEvent,
            ZombieTrickPhaseStartEvent,
        )
        from app.core_bak.entity.card import Fighter, Trick, Environment

        if isinstance(event, ZombiePhaseStartEvent):
            game.current_player.hand.activate(type=[Fighter])
        elif isinstance(event, PlantPhaseStartEvent):
            game.current_player.hand.activate(type=[Fighter, Trick, Environment])
        elif isinstance(event, ZombieTrickPhaseStartEvent):
            game.current_player.hand.activate(type=[Trick, Environment])

        return []


class HandDeactivateListener(Listener):
    def __init__(self, **kwargs):
        from app.core_bak.event.event_assemble import (
            ZombiePhaseEndEvent,
            PlantPhaseEndEvent,
            ZombieTrickPhaseEndEvent,
            CombatPhaseStartEvent,
        )

        super().__init__(**kwargs)

        self.on_events = [
            PlantPhaseEndEvent,
            ZombiePhaseEndEvent,
            ZombieTrickPhaseEndEvent,
            CombatPhaseStartEvent,
        ]
        self.lifetime = Lifetime.PERMANENT
        self.position = Position.highest_priority()

    def respond(self, event: Event, game: Game) -> Events:
        from app.core_bak.event.event_assemble import (
            ZombiePhaseEndEvent,
            PlantPhaseEndEvent,
            ZombieTrickPhaseEndEvent,
        )
        from app.core_bak.entity.card import Fighter, Trick, Environment

        if isinstance(event, ZombiePhaseEndEvent):
            game.current_player.hand.deactivate(type=[Fighter, Trick, Environment])
        elif isinstance(event, PlantPhaseEndEvent):
            game.current_player.hand.deactivate(type=[Fighter, Trick, Environment])
        elif isinstance(event, ZombieTrickPhaseEndEvent):
            game.current_player.hand.deactivate(type=[Fighter, Trick, Environment])

        return []
