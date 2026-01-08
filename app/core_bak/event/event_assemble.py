from app.core_bak import Events
from app.core_bak.engine.game import Game
from app.core_bak.event.event import Event
from app.core_bak.base import GamePhase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core_bak import Events
    from app.core_bak.engine.game import Game
    from app.core_bak.entity import Player, Card


class CardDrawEvent(Event):
    source: Player
    target: Card
    priority: int = 2

    def execute(self, game: "Game") -> Events:
        self.source.hand.cards.append(self.target)
        return []

    def cancel(self):
        self.source.deck.cards.insert(0, self.target)


class EnergyGainEvent(Event):
    target: Player
    amount: int
    priority: int = 2

    def execute(self, game: "Game") -> Events:
        self.target.energy += self.amount
        return []


class CardPlayEvent(Event):
    pass

    def execute(self, game: "Game") -> Events:
        return []


class ZombiePhaseEndEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return []


class ZombiePhaseStartEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        game.current_player = game.zombie_player
        game.phase = GamePhase.ZOMBIE_PHASE
        return [ZombiePhaseEndEvent()]


class PlantPhaseEndEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return []


class PlantPhaseStartEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return [PlantPhaseEndEvent()]


class ZombieTrickPhaseEndEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return []


class ZombieTrickPhaseStartEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return [ZombieTrickPhaseEndEvent()]


class TurnEndEvent(Event):
    priority: int = 7

    def execute(self, game: Game) -> Events:
        return []


class TurnStartEvent(Event):
    priority: int = 7

    def execute(self, game: Game) -> Events:
        if game.turn_count == 1:
            return [TurnEndEvent()]

        return [
            EnergyGainEvent(target=game.zombie_player, amount=game.turn_count),
            EnergyGainEvent(target=game.plant_player, amount=game.turn_count),
            ZombiePhaseStartEvent(),
            TurnEndEvent(),
        ]


class SurprisePhaseEndEvent(Event):
    priority: int = 0

    def execute(self, game: Game) -> Events:
        game.surprise_phase = False
        game.event_manager.unregister(self.data["listener"])
        return []


class SurprisePhaseStartEvent(Event):
    priority: int = 0

    def execute(self, game: Game) -> Events:
        from app.core_bak.event.listener_assemble import SurprisePhaseListener

        game.surprise_phase = True
        listener = SurprisePhaseListener()
        game.event_manager.register(listener)
        return [SurprisePhaseEndEvent(data={"listener": listener})]


class DamageBlockEvent(Event):
    source: Card
    target: Player
    amount: int
    priority: int = 1

    def execute(self, game: "Game") -> Events:
        return self.target.super_block.defend(game)


class HeroDieEvent(Event):
    target: Player
    priority: int = 0

    def execute(self, game: "Game") -> Events:
        return []


class HeroTakeDamageEvent(Event):
    source: Card
    target: Player
    amount: int
    priority: int = 1

    def execute(self, game: "Game") -> Events:
        self.target.health -= self.amount
        if self.target.health <= 0:
            self.target.health = 0
            return [HeroDieEvent(target=self.target)]

        return []


class HeroHurtEvent(Event):
    source: Card
    target: Player
    priority: int = 1

    def execute(self, game: Game) -> Events:
        return [
            DamageBlockEvent(source=self.source, target=self.target),
            HeroTakeDamageEvent(
                source=self.source, target=self.target, amount=self.amount
            ),
        ]


class PhaseEndEvent(Event):
    priority: int = 0

    def execute(self, game: Game) -> Events:
        from app.core_bak.base import GamePhase

        match game.phase:
            case GamePhase.ZOMBIE_PHASE:
                return [ZombiePhaseEndEvent()]
            case GamePhase.PLANT_PHASE:
                return [PlantPhaseEndEvent()]
            case GamePhase.ZOMBIE_TRICK_PHASE:
                return [ZombieTrickPhaseEndEvent()]
            case _:
                return []


class ActionExpireEvent(Event):
    def execute(self, game: Game) -> Events:
        return []


class CombatPhaseEndEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return []


class CombatPhaseStartEvent(Event):
    priority: int = 6

    def execute(self, game: Game) -> Events:
        return [CombatPhaseEndEvent()]
