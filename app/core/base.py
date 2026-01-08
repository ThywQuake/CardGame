from dataclasses import dataclass
from enum import Enum


class CardClass(Enum):
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

    @property
    def opponent(self):
        if self == Faction.ZOMBIE:
            return Faction.PLANT
        elif self == Faction.PLANT:
            return Faction.ZOMBIE
        else:
            return Faction.NEUTRAL

    @property
    def number(self) -> int:
        match self:
            case Faction.ZOMBIE:
                return 1
            case Faction.PLANT:
                return 2
            case Faction.NEUTRAL:
                return 0


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
    UNHURTABLE: bool = False
    FRENZY: bool = False
    DEADLY: bool = False
    TOMB: bool = False
    FUSIONABLE: bool = False

    ARMOURED: int = 0
    ANTI_HERO: int = 0
    SPLASH_DAMAGE: int = 0
    OVERSHOOT: int = 0

    def special_strength(self) -> str | None:
        attack_keys = [
            "BULLSEYE",
            "DOUBLE_STRIKE",
            "STRIKETHROUGH",
            "FRENZY",
            "DEADLY",
            "ANTI_HERO",
            "OVERSHOOT",
        ]
        specials = []
        for key in attack_keys:
            value = getattr(self, key)
            if isinstance(value, bool) and value:
                specials.append(key)
            elif isinstance(value, int) and value > 0:
                specials.append(f"{key}({value})")
        match len(specials):
            case 0:
                return None
            case 1:
                return specials[0]
            case _:
                return "Complex"

    def special_defense(self) -> str | None:
        defense_keys = ["HEALTH_ATTACK", "UNTRICKABLE", "UNHURTABLE", "ARMOURED"]
        specials = []
        for key in defense_keys:
            value = getattr(self, key)
            if isinstance(value, bool) and value:
                specials.append(key)
            elif isinstance(value, int) and value > 0:
                specials.append(f"{key}({value})")
        match len(specials):
            case 0:
                return None
            case 1:
                return specials[0]
            case _:
                return "Complex"


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
class CardConfig:
    name: str
    description: str
    faction: Faction
    art_path: str

    cost: int
    card_class: CardClass
    rarity: Rarity
    pack: Pack
    tag: list[Label]

    strength: int | None = None
    health: int | None = None


@dataclass
class FighterState:
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

    ABILITIES: Ability = Ability()


@dataclass
class HeroConfig:
    name: str
    description: str
    faction: Faction
    art_path: str
    classes: list[CardClass]

    health: int = 20
