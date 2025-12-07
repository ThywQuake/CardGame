from abc import ABC, abstractmethod
from .event import Event
from typing import TYPE_CHECKING
from enum import Enum
if TYPE_CHECKING:
    from typing import List
    from .event import Object, Events
    from app.core.engine.game import Game




class Listener(ABC):
    def __init__(self, **kwargs):
        self.game: Game = kwargs.get("game", Game())
        self.source: Object = kwargs.get("source", None)
        self.on_events: List[Event] = kwargs.get("on_events", [])
        self.lifetime: Lifetime = kwargs.get("lifetime", Lifetime.PERMANENT)
        
    @abstractmethod
    def respond(self, event: Event) -> Events:
        pass
    
    def handle(self, event: Event) -> Events:
        if type(event) in self.on_events:
            return self.respond(event)
        return None
    
    @abstractmethod
    def unregister(self):
        pass