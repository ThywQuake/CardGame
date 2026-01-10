from app.core.event.event import Event
from app.core.base import Faction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game
    from app.core.item.card import Card


class EndPhaseEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        return []


class LaneCombatEndingEvent(Event):
    def __init__(self, lane_idx: int, **kwargs):
        super().__init__(**kwargs)
        self.lane_id = lane_idx
        self.priority = 5

    def execute(self, game: Game) -> Events:
        return []


class LaneCombatStartingEvent(Event):
    def __init__(self, lane_idx: int, **kwargs):
        super().__init__(**kwargs)
        self.lane_idx = lane_idx
        self.priority = 5

    def execute(self, game: Game) -> Events:
        return []


class AttackEvent(Event):
    def __init__(self, attacker_id: str, defender_id: str, damage: int, **kwargs):
        super().__init__(**kwargs)
        self.source_id = attacker_id
        self.target_id = defender_id
        self.amount = damage

    def execute(self, game: Game) -> Events: ...


class CombatPhaseStartingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        return []


class CombatPhaseEndingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        return []


class ZombiePhaseStartingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        energy = game.zombie_player.energy

        def playable(card: Card):
            return card.cost <= energy and card.subtype == "FighterCard"

        playable_cards = game.item_manager.filter(playable, ["z_hand"])

        game.item_manager._activate_end_phase_button(Faction.ZOMBIE)
        game.item_manager.activate(playable_cards, Faction.ZOMBIE)

        return []


class ZombiePhaseEndingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        z_hand = game.item_manager["z_hand"]
        game.item_manager.deactivate(z_hand)

        return []


class PlantPhaseStartingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        energy = game.plant_player.energy

        def playable(card: Card):
            return card.cost <= energy

        playable_cards = game.item_manager.filter(playable, ["p_hand"])
        game.item_manager._activate_end_phase_button(Faction.PLANT)
        game.item_manager.activate(playable_cards, Faction.PLANT)

        return []


class PlantPhaseEndingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        p_hand = game.item_manager["p_hand"]
        game.item_manager.deactivate(p_hand)

        return []


class ZombieTrickPhaseStartingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        energy = game.zombie_player.energy

        def playable(card: Card):
            return card.cost <= energy and card.subtype in ["TrickCard", "EnvCard"]

        playable_cards = game.item_manager.filter(playable, ["z_hand"])
        game.item_manager._activate_end_phase_button(Faction.ZOMBIE)
        game.item_manager.activate(playable_cards, Faction.ZOMBIE)

        return []


class ZombieTrickPhaseEndingEvent(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority = 6

    def execute(self, game: Game) -> Events:
        z_hand = game.item_manager["z_hand"]
        game.item_manager.deactivate(z_hand)

        return []
