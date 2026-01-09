from abc import ABC, abstractmethod
from .event import Event
from app.core.base import Lifetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from .event import Events
    from app.core.engine.game import Game
from app.core.item.target import Fighter, Env


class Listener(ABC):
    def __init__(self, **kwargs):
        self.source: Fighter | Env | None = kwargs.get("source", None)
        self.on_events: List[str] = kwargs.get("on_events", [])
        self.lifetime: Lifetime = kwargs.get("lifetime", Lifetime.ONCE)
        self.end: bool = False

    @abstractmethod
    def respond(self, event: Event, game: Game) -> Events:
        pass

    def handle(self, event: Event, game: Game) -> Events:
        if event.name in self.on_events:
            response = self.respond(event, game)
            if response:
                if self.lifetime == Lifetime.ONCE:
                    self.end = True
            return response
        return []

    @property
    def pos(self) -> tuple[int, int, int, int]:
        from app.core.item.target import Fighter, Env

        if isinstance(self.source, Fighter):
            pos = self.source.on_pos
            if pos:
                return (1, pos.lane, pos.faction.number, pos.index)
        elif isinstance(self.source, Env):
            lane = self.source.on_lane
            if lane:
                return (1, lane.lane, 0, 0)
        return (0, 0, 0, 0)

    def validate(self, game: Game) -> bool:
        if self.end:
            return False

        if self.source is None:
            return True

        source_id = self.source.id
        if source_id in game.item_manager._indices:
            return True

        return False
