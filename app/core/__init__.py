from typing import Optional, Union, List
from app.core.engine.game import Game
from app.core.entity import Player, Card
from app.core.event.event import Event


Object = Optional[Union[Game, Player, Card]]
Events = Optional[Union[Event, List[Event]]]

