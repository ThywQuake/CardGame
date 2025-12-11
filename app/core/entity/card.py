from abc import ABC, abstractmethod
from uuid import uuid4
from app.core.config import Config, FighterConfig, TrickConfig, EnvironmentConfig
from typing import List, TYPE_CHECKING, Optional
from app.core.event.listener import Listener
from app.core.entity.state import FighterState, EnvironmentState
from app.core.base import Position, PFaction

if TYPE_CHECKING:
    from app.core.entity.ability import Ability
    from app.core.base import Position


class Card(ABC):
    def __init__(self, **kwargs):
        self.config: Optional[type[Config]] = kwargs.get("config", None)
        if self.config is not None:
            self.position.FACTION = PFaction.map(self.config.FACTION)

    def _on_board(self, **kwargs):
        """
        When the card is ready for the battlefield, do some setup here.
        Otherwise, card is for info storage only.
        """

        self.game_id: int = int(uuid4())
        self.position: Position = kwargs.get("position", Position())
        self.in_deck_listeners: List[Listener] = kwargs.get("in_deck_listeners", [])
        self.in_hand_listeners: List[Listener] = kwargs.get("in_hand_listeners", [])
        self.from_play_listeners: List[Listener] = kwargs.get("from_play_listeners", [])
        self.in_deck: bool = True
        self.in_hand: bool = False
        self.in_field: bool = False
        self.in_graveyard: bool = False

        self.selectable: bool = False
        self.playable_positions: List[Position] = []
        self.visible: bool = True

        self.abilities: List[Ability] = kwargs.get("abilities", [])
        self.bundle_abilities(self.abilities)

    def _bundle_ability(self, ability: Ability):
        from app.core.base import Lifetime

        ability.source = self
        ability.position = self.position
        match ability.lifetime:
            case Lifetime.IN_DECK:
                self.in_deck_listeners.append(ability)
            case Lifetime.IN_HAND:
                self.in_hand_listeners.append(ability)
            case Lifetime.IN_FIELD | Lifetime.PERMANENT | Lifetime.ONCE:
                self.from_play_listeners.append(ability)
            case _:
                self.from_play_listeners.append(ability)

    def bundle_abilities(self, abilities: List[Ability]):
        for ability in abilities:
            self._bundle_ability(ability)

    def unbundle_ability(self, ability: Ability):
        from app.core.base import Lifetime

        match ability.lifetime:
            case Lifetime.IN_DECK:
                self.in_deck_listeners.remove(ability)
            case Lifetime.IN_HAND:
                self.in_hand_listeners.remove(ability)
            case Lifetime.IN_FIELD | Lifetime.PERMANENT | Lifetime.ONCE:
                self.from_play_listeners.remove(ability)
            case _:
                self.from_play_listeners.remove(ability)

    def update_position(self, position: Position):
        self.position = position
        for ability in self.abilities:
            ability.position = position

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def on_board(self, **kwargs):
        pass


class Fighter(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_board(self, **kwargs):
        self._on_board(**kwargs)
        assert isinstance(self.config, FighterConfig)

        self.state: FighterState = FighterState()
        self.state.load(
            cost=self.config.COST,
            strength=self.config.STRENGTH,
            health=self.config.HEALTH,
        )


class Trick(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_board(self, **kwargs):
        self._on_board(**kwargs)
        assert isinstance(self.config, TrickConfig)

        # Tricks may have states in future updates
        self.state = None


class Environment(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_board(self, **kwargs):
        self._on_board(**kwargs)
        assert isinstance(self.config, EnvironmentConfig)

        self.state: EnvironmentState = EnvironmentState()
        self.state.load(cost=self.config.COST)
