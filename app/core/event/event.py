from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.core.engine.game import Game
    from app.core import Object, Events

class Event(ABC):
    def __init__(self, **kwargs):
        self.game: Game = kwargs.get("game", Game())
        self.source: Object = kwargs.get("source", None)
        self.target: Object = kwargs.get("target", None)
        self.cancelled: bool = False

    @abstractmethod
    def excute(self) -> Events:
        pass
    
    def cancel(self):
        self.cancelled = True
        pass