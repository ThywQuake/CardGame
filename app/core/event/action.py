from typing import TYPE_CHECKING, Optional
from abc import abstractmethod, ABC
from app.core.base import Position
from time import sleep

if TYPE_CHECKING:
    from app.core import Events, Object
    from app.core.entity import Player


class Action(ABC):
    def _parse(self, **kwargs):
        self.actor: Optional[Player] = kwargs.get("actor", None)
        self.target: Object = kwargs.get("target", None)
        self.position: Optional[Position] = kwargs.get("position", None)
        self.data: dict = kwargs.get("data", {})

    @abstractmethod
    def collect(self, **kwargs) -> Events:
        while True:
            action: dict = self.listen()
            if action and self._validate(**action):
                self._parse(**kwargs)
                return self._generate_events()
            else:
                sleep(0.1)

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


class CardPlayAction(Action): ...
