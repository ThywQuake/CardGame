from app.core.event.listener import Listener
from app.core.base import Lifetime
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.event.event import Event
    from app.core import Events


class Ability(Listener):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lifetime = Lifetime.IN_FIELD

    @abstractmethod
    def respond(self, event: Event) -> Events:
        pass
