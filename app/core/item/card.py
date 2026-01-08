from app.core.item.item import Item
from app.core.item.target import Fighter, Env
from app.core.base import CardConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.event.listener import Listener


class Card(Item):
    def __init__(self, card_config: CardConfig, **kwargs):
        super().__init__(**kwargs)
        self.type = "Card"

        for key, value in card_config.__dict__.items():
            if value is not None:
                setattr(self, key, value)

        self.abilities: dict[str, Listener] = {}

    def add_ability(self, name: str, ability: Listener):
        self.abilities[name] = ability


class FighterCard(Card):
    def __init__(self, card_config: CardConfig, fighter: Fighter, **kwargs):
        super().__init__(card_config, **kwargs)
        self.subtype = "FighterCard"

        self.fighter = fighter


class EnvCard(Card):
    def __init__(self, card_config: CardConfig, env: Env, **kwargs):
        super().__init__(card_config, **kwargs)
        self.subtype = "EnvCard"

        self.env = env


class TrickCard(Card):
    def __init__(self, card_config: CardConfig, **kwargs):
        super().__init__(card_config, **kwargs)
        self.subtype = "TrickCard"
