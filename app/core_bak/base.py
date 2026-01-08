from dataclasses import dataclass, field
from enum import Enum
from random import randint


class Type(Enum):
    TOKEN = "TOKEN"

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


class Lifetime(Enum):
    PERMANENT = "PERMANENT"
    IN_DECK = "IN_DECK"
    IN_HAND = "IN_HAND"
    IN_FIELD = "IN_FIELD"

    ONCE = "ONCE"


@dataclass
class Config:
    NAME: str = "Unnamed"
    TYPE: Type = Type.BEASTY
    FACTION: Faction = Faction.NEUTRAL
    DESCRIPTION: str = "No description."
    LABELS: list[Label] = list()
    ART_PATH: str = "path/to/art.png"
    PACK: Pack = Pack.BASIC
    RARITY: Rarity = Rarity.COMMON


@dataclass
class FighterConfig(Config):
    COST: int = 1
    STRENGTH: int = 1
    HEALTH: int = 1
    TRAIT: Trait = field(default_factory=Trait)


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
        self.ID = randint(int(1e8), int(1e9) - 1)
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
        self.ID = randint(int(1e8), int(1e9) - 1)


class PZone(Enum):
    DECK = 0
    HAND = 1
    FIELD = 2
    GRAVEYARD = 3


class PLane(Enum):
    WHOLE_FIELD = 0
    LANE_1 = 1
    LANE_2 = 2
    LANE_3 = 3
    LANE_4 = 4
    LANE_5 = 5
    OTHER = 6

    def index(self):
        if self in [
            PLane.LANE_1,
            PLane.LANE_2,
            PLane.LANE_3,
            PLane.LANE_4,
            PLane.LANE_5,
        ]:
            return self.value - 1
        else:
            return -1


class PFaction(Enum):
    WHOLE_LANE = 0
    ENVIRONMENT = 1
    ZOMBIE = 2
    PLANT = 3
    OTHER = 4

    @staticmethod
    def map(faction: Faction):
        match faction:
            case Faction.ZOMBIE:
                return PFaction.ZOMBIE
            case Faction.PLANT:
                return PFaction.PLANT
            case _:
                return PFaction.OTHER


class PSeat(Enum):
    ZOMBIE_SEAT = 0
    PLANT_FRONT_SEAT = 1
    PLANT_BACK_SEAT = 2
    OTHER_SEAT = 3

    def index(self):
        if self in [PSeat.PLANT_FRONT_SEAT, PSeat.PLANT_BACK_SEAT]:
            return self.value - 2
        elif self == PSeat.ZOMBIE_SEAT:
            return 0
        else:
            return -1

    def another(self):
        if self == PSeat.PLANT_FRONT_SEAT:
            return PSeat.PLANT_BACK_SEAT
        elif self == PSeat.PLANT_BACK_SEAT:
            return PSeat.PLANT_FRONT_SEAT
        else:
            return PSeat.OTHER_SEAT


class PFusion(Enum):
    NON_FUSION = 0
    FUSION = 1
    OTHER = 2


@dataclass
class Position:
    """
    ZONE:
    - 0: DECK
    - 1: HAND
    - 2: FIELD
    - 3: GRAVEYARD

    LANE:
    - 0: whole-field
    - 1-5: field lane index
    - 6: other

    FACTION:
    - 0: whole-lane(for tricks)
    - 1: environment
    - 2: zombie faction
    - 3: plant faction
    - 4: other

    SEAT:
    - for ZOMBIE: 0
    - for PLANT: 0(FRONT), 1(BACK)
    - for others: 2

    FUSION:
    - 0: non-fusion
    - 1: fusion
    - 2: other
    """

    ZONE: PZone = PZone(0)
    LANE: PLane = PLane(6)
    FACTION: PFaction = PFaction(0)
    SEAT: PSeat = PSeat(2)
    FUSION: PFusion = PFusion(2)

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Position)
            and self.ZONE == value.ZONE
            and self.LANE == value.LANE
            and self.FACTION == value.FACTION
            and self.SEAT == value.SEAT
            and self.FUSION == value.FUSION
        )

    def __lt__(self, value: object) -> bool:
        if not isinstance(value, Position):
            return NotImplemented
        return (
            self.ZONE.value,
            self.LANE.value,
            self.FACTION.value,
            self.SEAT.value,
            self.FUSION.value,
        ) < (
            value.ZONE.value,
            value.LANE.value,
            value.FACTION.value,
            value.SEAT.value,
            value.FUSION.value,
        )

    @staticmethod
    def highest_priority():
        return Position(
            ZONE=PZone(0),
            LANE=PLane(0),
            FACTION=PFaction(0),
            SEAT=PSeat(0),
            FUSION=PFusion(0),
        )


class GamePhase(Enum):
    INITIAL_DRAW = "INITIAL_DRAW"
    ZOMBIE_PHASE = "ZOMBIE_PHASE"
    PLANT_PHASE = "PLANT_PHASE"
    ZOMBIE_TRICK_PHASE = "ZOMBIE_TRICK_PHASE"
    COMBAT_PHASE = "COMBAT_PHASE"
    SUPRISE_PHASE = "SUPRISE_PHASE"
    TURN_START = "TURN_START"
    TURN_END = "TURN_END"

    IDLE = "IDLE"


@dataclass
class GameState:
    TURN: int = 0
    PHASE: GamePhase = GamePhase.INITIAL_DRAW
    END: bool = False
    WINNER: Faction = Faction.NEUTRAL
