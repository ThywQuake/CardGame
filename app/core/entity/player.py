from app.core.base import Faction, Position
from app.core.entity.slot import Deck, Hand, Graveyard
from app.core.entity.hero import Hero
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events


class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Player")
        self.faction: Faction = kwargs.get("faction", Faction.ZOMBIE)

        self.deck: Deck = kwargs.get("deck", Deck())
        self.hand: Hand = kwargs.get("hand", Hand())
        self.graveyard: Graveyard = kwargs.get("graveyard", Graveyard())

        self.hero: Hero = kwargs.get("hero", Hero())

    def play_card(self, card_index: int, position: Position) -> Events: ...
