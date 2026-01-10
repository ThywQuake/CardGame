from app.core.event.event import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game


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
