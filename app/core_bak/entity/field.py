from app.core_bak.base import Position
from app.core_bak.entity.card import Fighter, Environment
from typing import List, TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    Zombies = List[Optional[Fighter]]
    Plants = List[List[Optional[Fighter]]]
    Environments = List[Optional[Environment]]


class Field:
    def __init__(self, **kwargs):
        self.zombies: Zombies = kwargs.get("zombies", [None] * 5)
        self.plants: Plants = kwargs.get("plants", [[None] * 2 for _ in range(5)])
        self.environments: Environments = kwargs.get("environments", [None] * 5)

    def __getitem__(self, position: Position) -> Optional[Union[Fighter, Environment]]:
        from app.core_bak.base import PZone, PFaction

        if not position.ZONE == PZone.FIELD:
            return None
        match position.FACTION:
            case PFaction.ZOMBIE:
                return self.zombies[position.LANE.index()]
            case PFaction.PLANT:
                return self.plants[position.LANE.index()][position.SEAT.index()]
            case PFaction.ENVIRONMENT:
                return self.environments[position.LANE.index()]
        return None
