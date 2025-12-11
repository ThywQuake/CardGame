from app.core.base import Faction, Rarity, Type, Pack
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.core.entity.ability import Ability


def parse_config(config_path: str) -> dict:
    import json

    with open(config_path, "r") as f:
        data = json.load(f)
    return data


@dataclass
class Config(ABC):
    FACTION: Faction = Faction.NEUTRAL
    NAME: str = "TOKEN"
    DESCRIPTION: str = "Empty card has no description. Oh, isn't it a description?"
    ART_PATH: str = "app/asset/card_face/token.png"

    def _read_base(self, **kwargs):
        self.FACTION = Faction(kwargs.get("faction", "NEUTRAL"))
        self.NAME = kwargs.get("name", self.NAME)
        self.DESCRIPTION = kwargs.get("description", self.DESCRIPTION)
        self.ART_PATH = kwargs.get("art_path", self.ART_PATH)

    @abstractmethod
    def _read(self, **kwargs):
        pass

    def read(self, config_path: str):
        data = parse_config(config_path)
        self._read(**data)

    def _read_abilities(self, abilities: List[dict]):
        from app.core.entity.ability_assemble import __dict__

        for ability in abilities:
            if ability["name"] in __dict__:
                ability_class = __dict__[ability["name"]]
                yield ability_class(**ability.get("params", {}))


@dataclass
class FighterConfig(Config):
    COST: int = 0
    STRENGTH: int = 0
    HEALTH: int = 0
    ABILITIES: List["Ability"] = []
    RARITY: Rarity = Rarity.TOKEN
    PACK: Pack = Pack.BASIC
    TYPE: Type = Type.TOKEN

    def _read(self, **kwargs):
        self._read_base(**kwargs)
        self.COST = kwargs.get("cost", self.COST)
        self.STRENGTH = kwargs.get("strength", self.STRENGTH)
        self.HEALTH = kwargs.get("health", self.HEALTH)
        self.ABILITIES = list(self._read_abilities(kwargs.get("abilities", [])))
        self.RARITY = Rarity(kwargs.get("rarity", self.RARITY.value))
        self.PACK = Pack(kwargs.get("pack", self.PACK.value))
        self.TYPE = Type(kwargs.get("type", self.TYPE.value))


@dataclass
class TrickConfig(Config):
    COST: int = 0
    ABILITIES: List["Ability"] = []
    RARITY: Rarity = Rarity.TOKEN
    PACK: Pack = Pack.BASIC
    TYPE: Type = Type.TOKEN

    def _read(self, **kwargs):
        self._read_base(**kwargs)
        self.COST = kwargs.get("cost", self.COST)
        self.ABILITIES = list(self._read_abilities(kwargs.get("abilities", [])))
        self.RARITY = Rarity(kwargs.get("rarity", self.RARITY.value))
        self.PACK = Pack(kwargs.get("pack", self.PACK.value))
        self.TYPE = Type(kwargs.get("type", self.TYPE.value))


@dataclass
class EnvironmentConfig(Config):
    COST: int = 0
    ABILITIES: List["Ability"] = []
    RARITY: Rarity = Rarity.TOKEN
    PACK: Pack = Pack.BASIC
    TYPE: Type = Type.TOKEN

    def _read(self, **kwargs):
        self._read_base(**kwargs)
        self.COST = kwargs.get("cost", self.COST)
        self.ABILITIES = list(self._read_abilities(kwargs.get("abilities", [])))
        self.RARITY = Rarity(kwargs.get("rarity", self.RARITY.value))
        self.PACK = Pack(kwargs.get("pack", self.PACK.value))
        self.TYPE = Type(kwargs.get("type", self.TYPE.value))


@dataclass
class HeroConfig(Config):
    TYPE_A: Type = Type.TOKEN
    TYPE_B: Type = Type.TOKEN
    ABILITIES: List["Ability"] = []

    def _read(self, **kwargs):
        self._read_base(**kwargs)
        self.TYPE_A = Type(kwargs.get("type_a", self.TYPE_A.value))
        self.TYPE_B = Type(kwargs.get("type_b", self.TYPE_B.value))
        self.ABILITIES = list(self._read_abilities(kwargs.get("abilities", [])))
