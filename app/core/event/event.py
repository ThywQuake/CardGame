from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Object, Events
    from app.core.engine.game import Game


class Event(ABC):
    def __init__(self, **kwargs):
        self.source: Object = kwargs.get("source", None)
        self.target: Object = kwargs.get("target", None)
        self.cancelled: bool = False

    @abstractmethod
    def execute(self, game: Game) -> Events:
        pass

    def cancel(self):
        self.cancelled = True
        pass
