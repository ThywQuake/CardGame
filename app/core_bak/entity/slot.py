from abc import ABC
from app.core_bak.entity.card import Card
from typing import List, Optional


class Slot(ABC):
    def __init__(self, **kwargs):
        self.cards: List[Card] = kwargs.get("cards", [])
        self.size: int = kwargs.get("size", 40)


class Deck(Slot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _shuffle(self):
        from random import shuffle

        shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        self._shuffle()
        if len(self.cards) == 0:
            return None
        return self.cards.pop(0)


class Hand(Slot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size: int = kwargs.get("size", 10)

    def add_card(self, card: Card) -> bool:
        if len(self.cards) >= self.size:
            return False
        self.cards.append(card)
        return True

    def __getitem__(self, index: int) -> Card:
        return self.cards[index]

    def activate(self, type: List[type]):
        for card in self.cards:
            if card.__class__ in type:
                card.activate()

    def deactivate(self, type: List[type]):
        for card in self.cards:
            if card.__class__ in type:
                card.deactivate()


class Graveyard(Slot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size: int = kwargs.get("size", 9999)

    def bury(self, card: Card) -> None:
        self.cards.append(card)
