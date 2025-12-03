from abc import ABC, abstractmethod
from app.game.base import *
from queue import Queue
from random import shuffle


class GameEndingException(Exception):
    def __init__(self, winner: Faction):
        self.winner = winner
        super().__init__(f"Game ended! Winner: {winner}")


class Event(ABC):
    def __init__(self, **kwargs):
        self.source = kwargs.get("source", None)
        self.canceled = False

    @abstractmethod
    def execute(self, **kwargs):
        pass

    @abstractmethod
    def undo(self, **kwargs):
        pass


class Listener(ABC):
    def __init__(self, **kwargs):
        self.source = kwargs.get("source", None)
        self.interested_events: list[type[Event]] = kwargs.get("interested_events", [])
        self.absolute_position: AbsolutePosition = kwargs.get(
            "absolute_position", AbsolutePosition()
        )

    @abstractmethod
    def react(self, event: Event, **kwargs):
        pass


class EventManager:
    def __init__(self, **kwargs):
        self.game = kwargs.get("game", None)
        self.listeners: list[Listener] = kwargs.get("listeners", [])
        self.event_queue: Queue[Event] = Queue()

    def register(self, listener: Listener):
        self.listeners.append(listener)
        self.listeners.sort(key=lambda l: l.absolute_position)

    def unregister(self, listener: Listener):
        self.listeners.remove(listener)
        self.listeners.sort(key=lambda l: l.absolute_position)

    def notify(self, event: Event | list[Event]):
        if isinstance(event, list):
            for e in event:
                self.event_queue.put(e)
        else:
            self.event_queue.put(event)
        while not self.event_queue.empty():
            current_event = self.event_queue.get()
            sequence_event = current_event.execute()
            self.check_ending()

            for listener in self.listeners:
                if type(current_event) in listener.interested_events:
                    response = listener.react(current_event)
                    if current_event.canceled:
                        current_event.undo()
                        break
                    elif sequence_event is not None:
                        self.event_queue.put(sequence_event)

                    if response is not None:
                        self.event_queue.put(response)

    def check_ending(self):
        if self.game.ZP.hero.health <= 0:
            raise GameEndingException(Faction.PLANT)
        if self.game.PP.hero.health <= 0:
            raise GameEndingException(Faction.ZOMBIE)


class DrawEvent(Event):
    def __init__(self, player: "Player", card: "Card", **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.card = card

    def execute(self, **kwargs):
        if self.player.hand.capacity <= len(self.player.hand.cards):
            self.canceled = True
            return
        self.player.hand.get(self.card)

    def undo(self, **kwargs):
        self.player.deck.get(self.card)


class EnergyGainEvent(Event):
    def __init__(self, player: "Player", amount: int, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.amount = amount

    def execute(self, **kwargs):
        self.player.energy = self.amount

    def undo(self, **kwargs):
        pass


"--------------------------------------------------------------------------------------"


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


class TokenFighter(Fighter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def enter_field(self, **kwargs):
        pass

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

    def add_fighter(self, fighter: Fighter, faction: Faction, lane: int, seat: int = 0):
        if not (0 <= lane < 5):
            return False

        if faction == Faction.ZOMBIE:
            if self.zombies[lane] is None:
                self.zombies[lane] = fighter
                fighter.enter_field()
                return True
        elif faction == Faction.PLANT:
            if self.plants[lane][seat] is None:
                self.plants[lane][seat] = fighter
                fighter.enter_field()
                return True
        return False


class Card(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", CardConfig())
        self.cost = self.config.COST
        self.name = self.config.NAME

    @abstractmethod
    def play(self, **kwargs):
        pass


class FighterCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fighter: Fighter = kwargs.get("fighter", TokenFighter())

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
        self.capacity: int = kwargs.get("capacity", 0)

    def get(self, card: Card) -> bool:
        self.cards.append(card)


class Deck(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capacity = 100
        self.shuffle()

    def shuffle(self):
        shuffle(self.cards)

    def draw(self):
        if len(self.cards) == 0:
            return None
        return self.cards.pop(0)

    def get(self, card: Card):
        self.cards.append(card)
        self.shuffle()


class Hand(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capacity = 10


class Graveyard(CardSlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capacity = 200


class Hero:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Hero")
        self.health: int = kwargs.get("health", 20)

        self.art_path: str = kwargs.get("art_path", "")
        self.super_powers: list[Card] = kwargs.get("super_powers", [TrickCard()] * 4)
        shuffle(self.super_powers)

    def draw(self) -> Card:
        if len(self.super_powers) == 0:
            return None
        return self.super_powers.pop(0)


class SuperBlock:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "SuperBlock")
        self.description: str = kwargs.get("description", "")
        self.art_path: str = kwargs.get("art_path", "")


class Player:
    def __init__(self, **kwargs):
        self.name: str = kwargs.get("name", "Player")
        self.hero: Hero = kwargs.get("hero", Hero())
        self.deck: Deck = kwargs.get("deck", Deck(cards=[FighterCard()] * 40))
        self.hand: Hand = kwargs.get("hand", Hand())
        self.graveyard: Graveyard = kwargs.get("graveyard", Graveyard())
        self.super_block: SuperBlock = kwargs.get("super_block", SuperBlock())
        self.energy: int = kwargs.get("energy", 0)

    def initial_draw(self) -> Event:
        cards = [self.deck.draw()] * 4
        super_power = self.hero.draw()
        cards.append(super_power)
        return [DrawEvent(player=self, card=card) for card in cards]

    def get_energy(self, amount: int) -> Event:
        return EnergyGainEvent(player=self, amount=amount)
