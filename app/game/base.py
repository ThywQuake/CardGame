from dataclasses import dataclass
from enum import Enum


class Type(Enum):
    BEASTY = "BEASTY"
    BRAINY = "BRAINY"
    CRAZY = "CRAZY"
    HEARTY = "HEARTY"
    SNEAKY = "SNEAKY"

    GUARDIAN = "GUARDIAN"
    KABLOOM = "KABLOOM"
    MEGAGROW = "MEGAGROW"
    SMARTY = "SMARTY"
    SOLAR = "SOLAR"


class Faction(Enum):
    ZOMBIE = "ZOMBIE"
    PLANT = "PLANT"
    NEUTRAL = "NEUTRAL"

    def opponent(self):
        if self == Faction.ZOMBIE:
            return Faction.PLANT
        elif self == Faction.PLANT:
            return Faction.ZOMBIE
        else:
            return Faction.NEUTRAL


@dataclass
class Ability:
    BULLSEYE: bool = False
    TEAM_UP: bool = False
    AMPHIBIOUS: bool = False
    HUNT: bool = False
    HEALTH_ATTACK: bool = False
    UNTRICKABLE: bool = False
    DOUBLE_STRIKE: bool = False
    STRIKETHROUGH: bool = False
    FRENZY: bool = False
    DEADLY: bool = False
    TOMB: bool = False
    FUSIONABLE: bool = False

    ARMOURED: int = 0
    ANTI_HERO: int = 0
    SPLASH_DAMAGE: int = 0
    OVERSHOOT: int = 0


class Label(Enum):
    ZOMBIE = "ZOMBIE"
    PLANT = "PLANT"
    TRICK = "TRICK"
    ENVIRONMENT = "ENVIRONMENT"
    TOKEN = "TOKEN"

    MIME = "MIME"
    PIRATE = "PIRATE"
    BARREL = "BARREL"
    FLYTRAP = "FLYTRAP"
    DRAGON = "DRAGON"
    BANANA = "BANANA"
    MOSS = "MOSS"
    CORN = "CORN"
    PINECONE = "PINECONE"
    SEED = "SEED"
    CACTUS = "CACTUS"
    TREE = "TREE"
    FLOWER = "FLOWER"
    MUSHROOM = "MUSHROOM"
    LEAFY = "LEAFY"
    BERRY = "BERRY"

    PROFESSIONAL = "PROFESSIONAL"
    PET = "PET"
    SCIENTIST = "SCIENTIST"
    HISTORIAN = "HISTORIAN"
    GARGANTUAR = "GARGANTUAR"

    CLOCK = "CLOCK"
    PARTY = "PARTY"
    MUSTACHE = "MUSTACHE"
    MONSTER = "MONSTER"

    PEA = "PEA"
    NUT = "NUT"
    SQUASH = "SQUASH"
    BEAN = "BEAN"
    SPORTS = "SPORTS"

    GOURMET = "GOURMET"
    FRUIT = "FRUIT"

    ANIMAL = "ANIMAL"
    DANCING = "DANCING"
    IMP = "IMP"


class Rarity(Enum):
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    SUPER_RARE = "SUPER_RARE"
    LEGENDARY = "LEGENDARY"
    EVENT = "EVENT"
    TOKEN = "TOKEN"


class Pack(Enum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"
    GALACTIC = "GALACTIC"
    COLOSSAL = "COLOSSAL"
    TRIASSIC = "TRIASSIC"


@dataclass
class FighterConfig:
    NAME: str
    TYPE: Type
    FACTION: Faction
    DESCRIPTION: str
    LABELS: list[Label]
    ART_PATH: str

    COST: int
    STRENGTH: int
    HEALTH: int
    ABILITIES: Ability
    RARITY: Rarity
    PACK: Pack


@dataclass
class FighterState:
    ID: int

    INITIAL_COST: int
    INITIAL_STRENGTH: int
    INITIAL_HEALTH: int

    CURRENT_COST: int
    CURRENT_STRENGTH: int
    CURRENT_HEALTH: int

    MAX_COST: int
    MAX_STRENGTH: int
    MAX_HEALTH: int

    IS_DAMAGED: bool = False
    IS_DESTROYED: bool = False

    IN_FIELD: bool = False
    IN_TOMB: bool = False

    # Debuffs
    FROZEN: bool = False
    DOOMED: bool = False
