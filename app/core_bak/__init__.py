from typing import Optional, Union, List
from app.core_bak.engine import Game
from app.core_bak.entity import Player, Card
from app.core_bak.event import Event, EventManager, Listener


Object = Optional[Union[Game, Player, Card]]
Events = List[Optional[Event]]

__all__ = [
    "Object",
    "Events",
    "Game",
    "Player",
    "Card",
    "Event",
    "EventManager",
    "Listener",
]
