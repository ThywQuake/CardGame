from abc import ABC, abstractmethod
from app.game.base import *


class Fighter(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", FighterConfig())
        self.state = FighterState(self.config)

    @abstractmethod
    def enter_field(self, **kwargs):
        pass

    @abstractmethod
    def leave_field(self, **kwargs):
        pass


class Environment(ABC):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "Environment")
        self.description = kwargs.get("description", "")
        self.art_path = kwargs.get("art_path", "")

    @abstractmethod
    def ability(self, **kwargs):
        pass


class HeightEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def ability(self):
        pass


class WaterEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def ability(self):
        pass


class Field:
    def __init__(self, game: "Game"):  # type: ignore quoted annotation
        self.zombies: list[Fighter | None] = [None] * 5
        self.plants: list[list[Fighter | None]] = [
            [None, None] for _ in range(5)
        ]  # 2 rows for plants
        self.environments: list[Environment | None] = [
            HeightEnv(),
            None,
            None,
            None,
            WaterEnv(),
        ]
        self.game: "Game" = game  # type: ignore quoted annotation


class Card(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", CardConfig())

    @abstractmethod
    def play(self, **kwargs):
        pass


class FighterCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fighter: Fighter = kwargs.get("fighter", Fighter())

    def play(self, **kwargs):
        pass


class TrickCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def play(self, **kwargs):
        pass


class EnvironmentCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.environment: Environment = kwargs.get("environment", Environment())

    def play(self, **kwargs):
        pass


class CardSlot(ABC):
    def __init__(self, **kwargs):
        self.cards: list[Card] = kwargs.get("cards", [])


class Deck(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Hand(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Graveyard(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Hero:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Hero")
        self.health: int = kwargs.get("health", 20)

        self.art_path: str = kwargs.get("art_path", "")


class SuperBlock:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "SuperBlock")
        self.description: str = kwargs.get("description", "")
        self.art_path: str = kwargs.get("art_path", "")


class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Player")
        self.hero: Hero = kwargs.get("hero", Hero())
        self.deck: Deck = kwargs.get("deck", Deck())
        self.hand: Hand = kwargs.get("hand", Hand())
        self.graveyard: Graveyard = kwargs.get("graveyard", Graveyard())
        self.super_blocks: list[SuperBlock] = kwargs.get("super_blocks", [])
