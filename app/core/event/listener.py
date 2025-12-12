from abc import ABC, abstractmethod
from .event import Event
from typing import TYPE_CHECKING
from app.core.base import Lifetime, Position

if TYPE_CHECKING:
    from typing import List
    from .event import Object, Events
    from app.core.engine.game import Game


class Listener(ABC):
    def __init__(self, **kwargs):
        self.source: Object = kwargs.get("source", None)
        self.on_events: List[type[Event]] = kwargs.get("on_events", [])
        self.lifetime: Lifetime = kwargs.get("lifetime", Lifetime.ONCE)
        self.end: bool = False
        self.position: Position = kwargs.get("position", Position())

    @abstractmethod
    def respond(self, event: Event, game: Game) -> Events:
        pass

    def handle(self, event: Event, game: Game) -> Events:
        if type(event) in self.on_events:
            if self.lifetime == Lifetime.ONCE:
                self.end = True
            return self.respond(event, game)
        return []
