from typing import TYPE_CHECKING, Optional
from abc import abstractmethod, ABC
from app.core.base import Position
from time import sleep, time

if TYPE_CHECKING:
    from app.core import Events, Object
    from app.core.entity import Player
    from app.core.engine.game import Game


class PhaseAction(ABC):
    def __init__(self, **kwargs):
        self.max_time: float = kwargs.get("max_time", 30)

    def _parse(self, **kwargs):
        self.source: Optional[Player] = kwargs.get("source", None)
        self.target: Object = kwargs.get("target", None)
        self.position: Optional[Position] = kwargs.get("position", None)
        self.data: dict = kwargs.get("data", {})
        self.amount: int = kwargs.get("amount", 0)
        self.type: str = kwargs.get("type", "")

    def collect(self, game: Game):
        accumulated_time: float = 0.0
        start = time()
        while accumulated_time < self.max_time:
            action: dict = self.listen()
            if action and self._validate(**action):
                self._parse(**action)
                events: Events = self._generate_events()

                accumulated_time += time() - start
                game.step(events)
                start = time()

            else:
                accumulated_time += time() - start
                sleep(0.1)
                start = time()

        game.step(game.phase_end())

    @abstractmethod
    def _validate(self, **kwargs) -> bool:
        """Validate if the action can be performed."""
        pass

    @abstractmethod
    def _generate_events(self) -> Events:
        """Generate events based on the action."""
        pass

    @abstractmethod
    def listen(self) -> dict:
        """Listen for an action input."""
        pass


class CardPlayAction(PhaseAction): ...


class PhaseEndAction(PhaseAction): ...
