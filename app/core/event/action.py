from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from app.core.base import Position

if TYPE_CHECKING:
    from app.core.event import Action
    from app.core import Events
from app.core.entity.card import Card


class Action(ABC):
    def __init__(self, **kwargs):
        from app.core.engine import Game

        self.game: Game = kwargs.get("game", Game())
        self.player = self.game.current_player

    @abstractmethod
    def __or__(self, other: Action) -> Events:
        pass


class SelectPositionInField(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position: Position = kwargs.get("position", Position())

    def __or__(self, other: Action) -> Events:
        return []


class SelectFighterInField(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position: Position = kwargs.get("position", Position())
        self.fighter = self.game.field[self.position]

    def __or__(self, other: Action) -> Events:
        return []


class SelectCardInHand(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_index: int = kwargs.get("card_index", -1)
        self.card: Card = self.player.hand[self.card_index]

    def __or__(self, other: Action) -> Events:
        if isinstance(other, SelectPositionInField):
            return self.player.play_card(self.card_index, other.position)
        return []
