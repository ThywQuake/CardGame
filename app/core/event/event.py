from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from app.core.engine.game import Game
    from app.core import Events


class Event(ABC):
    def __init__(self, **kwargs):
        """

        Event priority mapping:
        - level 0: Game Over Events + Surprise Phase Starting.
        - level 1: Critical Events (e.g., Hero Hurt)
        - level 2: High Priority Events (e.g., Card Draw, Energy Gain)
        - level 3: Normal Events (e.g., Card Play)
        - level 4: Pair Event: Surprise Phase Ending.
        - level 5: Pair Event: Lane Combat Starting/Ending.
        - level 6: Pair Event: Phase Starting/Ending.
        - level 7: Pair Event: Turn Starting/Ending.

        """

        self.id = str(uuid4())

        self.source_id: str | None = kwargs.get("source", None)
        self.target_id: str | None = kwargs.get("target", None)
        self.amount: int = kwargs.get("amount", 0)
        self.data: dict = kwargs.get("data", {})
        self.cancelled: bool = False
        self.priority: int = kwargs.get("priority", 3)

    @abstractmethod
    def execute(self, game: Game) -> Events:
        pass

    def cancel(self):
        self.cancelled = True

    @property
    def name(self) -> str:
        return self.__class__.__name__
