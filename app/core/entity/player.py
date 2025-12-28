from app.core.base import Faction, Position
from app.core.entity.slot import Deck, Hand, Graveyard
from app.core.entity.hero import Hero
from app.core.entity.super_block import SuperBlock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core import Events


class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Player")
        self.id: int = kwargs.get("id", 0)
        self.faction: Faction = kwargs.get("faction", Faction.ZOMBIE)

        self.deck: Deck = kwargs.get("deck", Deck())
        self.hand: Hand = kwargs.get("hand", Hand())
        self.graveyard: Graveyard = kwargs.get("graveyard", Graveyard())

        self.hero: Hero = kwargs.get("hero", Hero())
        self.super_block: SuperBlock = SuperBlock()

        self.energy: int = kwargs.get("energy", 0)
        self.health: int = kwargs.get("health", 20)

    def draw(self, count: int = 1) -> Events:
        from app.core.event.event_assemble import CardDrawEvent

        events: Events = []
        for _ in range(count):
            if not self.deck.cards:
                break
            card = self.deck.cards.pop(0)
            events.append(CardDrawEvent(source=self, target=card))

        return events

    def get_energy(self, amount: int) -> Events:
        from app.core.event.event_assemble import EnergyGainEvent

        return [EnergyGainEvent(source=self, amount=amount)]

    def opposite_faction(self) -> Faction:
        return Faction.PLANT if self.faction == Faction.ZOMBIE else Faction.ZOMBIE

    def play_card(self, card_index: int, position: Position) -> Events:
        from app.core.event.event_assemble import CardPlayEvent

        if card_index < 0 or card_index >= len(self.hand.cards):
            return []

        card = self.hand.cards[card_index]
        return [CardPlayEvent(source=self, target=card, position=position)]
