from dataclasses import dataclass
from enum import Enum
from random import randint
from functools import total_ordering


class Type(Enum):
    BEASTY = "BEASTY"
    BRAINY = "BRAINY"
    CRAZY = "CRAZY"
    HEARTY = "HEARTY"
    SNEAKY = "SNEAKY"

    GUARDIAN = "GUARDIAN"
    KABLOOM = "KABLOOM"
    MEGA_GROW = "MEGA_GROW"
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
class Trait:
    BULLSEYE: bool = False
    TEAM_UP: bool = False
    AMPHIBIOUS: bool = False
    HUNT: bool = False
    HEALTH_ATTACK: bool = False
    UNTRICKABLE: bool = False
    DOUBLE_STRIKE: bool = False
    STRIKETHROUGH: bool = False
    UNHURTABLE: bool = False
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
class Config:
    NAME: str = "Unnamed"
    TYPE: Type = Type.BEASTY
    FACTION: Faction = Faction.NEUTRAL
    DESCRIPTION: str = "No description."
    LABELS: list[Label] = None
    ART_PATH: str = "path/to/art.png"
    PACK: Pack = Pack.BASIC
    RARITY: Rarity = Rarity.COMMON


@dataclass
class FighterConfig(Config):
    COST: int = 1
    STRENGTH: int = 1
    HEALTH: int = 1
    TRAIT: Trait = Trait()


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

    ON_HEIGHT: bool = False
    ON_WATER: bool = False
    ON_PLAIN: bool = True
    ON_ENV: bool = False

    # buffs
    FROZEN: bool = False
    DOOMED: bool = False

    def __init__(self, config: FighterConfig):
        self.ID = randint(1e8, 1e9 - 1)
        self.INITIAL_COST = self.CURRENT_COST = self.MAX_COST = config.COST
        self.INITIAL_STRENGTH = self.CURRENT_STRENGTH = self.MAX_STRENGTH = (
            config.STRENGTH
        )
        self.INITIAL_HEALTH = self.CURRENT_HEALTH = self.MAX_HEALTH = config.HEALTH


@dataclass
class CardConfig(Config):
    COST: int = 1


@dataclass
class CardState:
    ID: int
    IN_DECK: bool = True
    IN_HAND: bool = False
    IN_GRAVEYARD: bool = False

    def __init__(self):
        self.ID = randint(1e8, 1e9 - 1)


@dataclass
class AbsolutePosition:
    """
    WHERE:
    - 0: DECK
    - 1: HAND
    - 2: FIELD
    - 3: GRAVEYARD

    LANE:
    - 1-5: field lane index
    - 0: non-field (deck, hand, graveyard)

    FACTION:
    - 0: NEUTRAL
    - 1: ZOMBIE
    - 2: PLANT

    SEAT:
    - for ZOMBIE: 0
    - for PLANT: 0(FRONT), 1(BACK)
    - for others: 0
    """

    WHERE: int = 0
    LANE: int = 0
    FACTION: int = 0
    SEAT: int = 0


class GamePhase(Enum):
    INITIAL_DRAW = "INITIAL_DRAW"
    ZOMBIE_PHASE = "ZOMBIE_PHASE"
    PLANT_PHASE = "PLANT_PHASE"
    ZOMBIE_TRICK_PHASE = "ZOMBIE_TRICK_PHASE"
    COMBAT_PHASE = "COMBAT_PHASE"
    SUPRISE_PHASE = "SUPRISE_PHASE"


@dataclass
class GameState:
    TURN: int = 0
    PHASE: GamePhase = GamePhase.INITIAL_DRAW
