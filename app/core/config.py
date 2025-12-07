from app.core.base import Faction, Rarity, Type, Pack
from abc import ABC
from dataclasses import dataclass


@dataclass
class CardConfig(ABC):
    FACTION: Faction = Faction.NEUTRAL
    NAME: str = "TOKEN"
    DESCRIPTION: str = "Empty card has no description. Oh, isn't it a description?"
    ART_PATH: str = "app/asset/card_face/token.png"

    def read_base(self, **kwargs):
        self.FACTION = Faction(kwargs.get("faction", "NEUTRAL"))
        self.NAME = kwargs.get("name", self.NAME)
        self.DESCRIPTION = kwargs.get("description", self.DESCRIPTION)
        self.ART_PATH = kwargs.get("art_path", self.ART_PATH)

    def read_abilities(self, abilities: list[dict]):
        for ability in abilities:
            pass


@dataclass
class FighterCardConfig(CardConfig):
    COST: int = 0
    STRENGTH: int = 0
    HEALTH: int = 0
    ABILITIES: list[dict] = []
    RARITY: Rarity = Rarity.TOKEN
    PACK: Pack = Pack.BASIC
    TYPE: Type = Type.TOKEN

    def read(self, **kwargs):
        self.read_base(**kwargs)
        self.COST = kwargs.get("cost", self.COST)
        self.STRENGTH = kwargs.get("strength", self.STRENGTH)
        self.HEALTH = kwargs.get("health", self.HEALTH)
        self.ABILITIES = kwargs.get("abilities", self.ABILITIES)
        self.RARITY = Rarity(kwargs.get("rarity", self.RARITY.value))
        self.PACK = Pack(kwargs.get("pack", self.PACK.value))
        self.TYPE = Type(kwargs.get("type", self.TYPE.value))

@dataclass
class TrickCardConfig(CardConfig):
    pass


@dataclass
class EnvCardConfig(CardConfig):
    pass