"""
What is an item?
An item is an object that can be dragged/selected by the player in the game interface.
So items must have a property indicating they are draggable/selectable or not, and the mask is bi-side for the two players!
Items can be cards, positions, heros, or even endphase button!
And also, items need to have an unique identity to distinguish them from others.
Abstracting items help to manage game interactions in a unified way.
"""

from uuid import uuid4
from abc import ABC
from app.core.base import Faction


class Item(ABC):
    def __init__(self, **kwargs):
        self.activated: dict[Faction, bool] = {
            Faction.PLANT: False,
            Faction.ZOMBIE: False,
        }
        self.id: str = str(uuid4())
        self.type: str = kwargs.get("type", "Item")

    def activate(self, faction: Faction):
        self.activated[faction] = True

    def deactivate(self, faction: Faction | None = None):
        if faction is None:
            for key in self.activated:
                self.activated[key] = False
        else:
            self.activated[faction] = False

    def is_activated(self, faction: Faction) -> bool:
        return self.activated[faction]
