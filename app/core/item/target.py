from app.core.item.item import Item
from app.core.item.position import Pos, Lane
from app.core.base import FighterState
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.item.card import Card
    from app.core.event.listener import Listener


class Target(Item):
    def __init__(self, proto_card: Card, **kwargs):
        super().__init__(**kwargs)
        self.type = "Target"

        self.proto_card: Card = proto_card
        self.abilities: dict[str, Listener] = {}

    def add_ability(self, name: str, ability: Listener):
        self.abilities[name] = ability

    @abstractmethod
    def bounce(self):
        pass


class Fighter(Target):
    def __init__(self, fighter_state: FighterState, proto_card: "Card", **kwargs):
        super().__init__(proto_card, **kwargs)
        self.subtype = "Fighter"

        self.state: FighterState = fighter_state
        self.on_pos: Pos | None = None

    def move_to(self, position: Pos):
        if self.on_pos is None:
            return
        self.on_pos.vacate()
        position.occupy_by(self.id)
        self.on_pos = position

    def bounce(self):
        if self.on_pos is None:
            return
        self.on_pos.vacate()
        return self.proto_card


class Env(Target):
    def __init__(self, proto_card: "Card", **kwargs):
        super().__init__(proto_card, **kwargs)
        self.subtype = "Env"

        self.on_lane: Lane | None = None

    def bounce(self):
        if self.on_lane is None:
            return
        if self.on_lane.coverer_id == self.id:
            self.on_lane.uncover()
        return self.proto_card
