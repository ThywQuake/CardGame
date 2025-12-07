from abc import ABC, abstractmethod
from app.core.base import Faction, PFaction, PZone, PLane, PSeat, PFusion, Position
from queue import Queue
from random import shuffle


class GameEndingException(Exception):
    def __init__(self, winner: Faction):
        self.winner = winner
        super().__init__(f"Game ended! Winner: {winner}")


class SurprisePhaseException(Exception):
    def __init__(self, player: "Player"):
        super().__init__(f"Surprise Phase: {player.name}")
        self.player = player


class Event(ABC):
    def __init__(self, **kwargs):
        self.source = kwargs.get("source", None)
        self.canceled = False

    @abstractmethod
    def execute(self, **kwargs) -> "Event" | list["Event"] | None:
        pass

    def undo(self, **kwargs) -> None:
        pass


class Listener(ABC):
    def __init__(self, **kwargs):
        self.source = kwargs.get("source", None)
        self.interested_events: list[type[Event]] = kwargs.get("interested_events", [])
        self.position: Position = kwargs.get("position", Position())

    @abstractmethod
    def react(self, event: Event, **kwargs) -> Event | list[Event] | None:
        pass


class EventManager:
    def __init__(self, **kwargs):
        self.game = kwargs.get("game", None)
        self.listeners: list[Listener] = kwargs.get("listeners", [])
        self.event_queue: Queue[Event] = Queue()

    def register(self, listener: Listener):
        self.listeners.append(listener)
        self.listeners.sort(key=lambda lsn: lsn.position)

    def unregister(self, listener: Listener):
        self.listeners.remove(listener)
        self.listeners.sort(key=lambda lsn: lsn.position)
    def notify(self, event: Event | list[Event]):
        if isinstance(event, list):
            for e in event:
                self.event_queue.put(e)
        else:
            self.event_queue.put(event)
        while not self.event_queue.empty():
            current_event = self.event_queue.get()
            if current_event is None:
                continue
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


class CardPlayEvent(Event):
    def __init__(self, player: "Player", card: "Card", **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.card = card

    def execute(self, **kwargs):
        self.player.hand.cards.remove(self.card)
        self.player.energy -= self.card.cost


class EnterFieldEvent(Event):
    def __init__(
        self, fighter: "Fighter", field: "Field", position: Position, **kwargs
    ):
        super().__init__(**kwargs)
        self.fighter = fighter
        self.field = field
        self.position = position

    def execute(self, **kwargs):
        self.field.add_fighter(self.fighter, self.position)
        return self.fighter.enter_field()


class SetEnvEvent(Event):
    def __init__(
        self, environment: "Environment", field: "Field", position: Position, **kwargs
    ):
        super().__init__(**kwargs)
        self.environment = environment
        self.field = field
        self.position = position

    def execute(self, **kwargs):
        former_env = self.field.environments[self.position.LANE.index()]
        former_env = None if former_env.is_env else former_env
        self.field.environments[self.position.LANE.index()] = self.environment
        return [
            self.environment.enter_field(),
            former_env.leave_field() if former_env is not None else None,
        ]


"--------------------------------------------------------------------------------------"


class Fighter(ABC):
    def __init__(self, **kwargs):
        self.config: FighterConfig = kwargs.get("config", FighterConfig())
        self.state: FighterState = FighterState(self.config)

    @abstractmethod
    def enter_field(self, **kwargs) -> Event | list[Event] | None:
        pass

    @abstractmethod
    def leave_field(self, **kwargs) -> Event | list[Event] | None:
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
        self.is_env = True

    @abstractmethod
    def enter_field(self, **kwargs):
        pass

    def leave_field(self, **kwargs):
        pass


class HeightEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_env = False

    def enter_field(self, **kwargs):
        pass


class LaneEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_env = False

    def enter_field(self, **kwargs):
        pass


class WaterEnv(Environment):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_env = False

    def enter_field(self, **kwargs):
        pass


class Field:
    def __init__(self, **kwargs):  # type: ignore quoted annotation
        self.zombies: list[Fighter | None] = [None] * 5
        self.plants: list[list[Fighter | None]] = [
            [None, None] for _ in range(5)
        ]  # 2 rows for plants
        self.default_environments: list[Environment] = [
            HeightEnv(),
            LaneEnv(),
            LaneEnv(),
            LaneEnv(),
            WaterEnv(),
        ]
        self.environments = self.default_environments.copy()
        # self.game: "Game" = game  # type: ignore quoted annotation

    def __getitem__(
        self, position: Position
    ) -> Fighter | list[Fighter | None] | Environment | None:
        if position.ZONE is not PZone.FIELD:
            return None
        if position.LANE not in [PLane.OTHER, PLane.WHOLE_FIELD]:
            if position.FACTION == PFaction.ZOMBIE:
                return self.zombies[position.LANE.index()]
            elif position.FACTION == PFaction.PLANT:
                if position.SEAT in [PSeat.PLANT_FRONT_SEAT, PSeat.PLANT_BACK_SEAT]:
                    return self.plants[position.LANE.index()][position.SEAT.index()]
            elif position.FACTION == PFaction.ENVIRONMENT:
                env = self.environments[position.LANE.index()]
                return env if env.is_env else None
            elif position.FACTION == PFaction.WHOLE_LANE:
                return [self.zombies[position.LANE.index()]] + self.plants[
                    position.LANE.index()
                ]

    def __setitem__(self, position: Position, object: Fighter | Environment | None):
        if position.ZONE is not PZone.FIELD:
            return
        if position.LANE not in [PLane.OTHER, PLane.WHOLE_FIELD]:
            if (
                position.FACTION == PFaction.ZOMBIE
                and isinstance(object, Fighter)
                and object.config.FACTION == Faction.ZOMBIE
                and (
                    (self[position] is None)
                    or (object is None)
                    or (
                        self[position] is not None and position.FUSION == PFusion.FUSION
                    )
                )
            ):
                self.zombies[position.LANE.index()] = object
            elif (
                position.FACTION == PFaction.PLANT
                and isinstance(object, Fighter)
                and object.config.FACTION == Faction.PLANT
                and position.SEAT in [PSeat.PLANT_FRONT_SEAT, PSeat.PLANT_BACK_SEAT]
            ):
                if self[position] is None or object is None:
                    self.plants[position.LANE.index()][position.SEAT.index()] = object
                elif self[position] is not None:
                    if position.FUSION == PFusion.FUSION:
                        self.plants[position.LANE.index()][
                            position.SEAT.index()
                        ] = object
                    elif (
                        position.FUSION == PFusion.NON_FUSION
                        and object.config.TRAIT.TEAM_UP
                    ):
                        temp = self[position]
                        self.plants[position.LANE.index()][
                            position.SEAT.index()
                        ] = object
                        # another plant pushed to another seat
                        self.plants[position.LANE.index()][
                            position.SEAT.another().index()
                        ] = temp
            elif position.FACTION == PFaction.ENVIRONMENT and isinstance(
                object, Environment
            ):
                self.environments[position.LANE.index()] = object

    def add_fighter(self, fighter: Fighter, position: Position):
        if self[position] is None:
            self[position] = fighter
        elif position.FUSION == PFusion.NON_FUSION and fighter.config.TRAIT.TEAM_UP:
            self[position] = fighter
        elif position.FUSION == PFusion.FUSION:
            ...
            # TODO: fusion logic is far more complex, extend later

    def play_card(
        self, player: "Player", card: "Card", target_position: Position
    ) -> Event:
        # if isinstance(card, FighterCard):
        #     fighter = card.fighter
        #     return [
        #         CardPlayEvent(player=player, card=card),
        #         EnterFieldEvent(fighter=fighter, field=self, position=target_position),
        #     ]
        # elif isinstance(card, TrickCard):
        #     ...
        return card.play(player=player, field=self, target_position=target_position)


class Card(ABC):
    def __init__(self, **kwargs):
        self.config = kwargs.get("config", CardConfig())
        self.cost = self.config.COST
        self.name = self.config.NAME
        self.playable = False
        self.valid_targets: list[Position] = []

    @abstractmethod
    def play(
        self, player: "Player", field: "Field", target_position: Position, **kwargs
    ):
        pass


class FighterCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fighter: Fighter = kwargs.get("fighter", TokenFighter())

    def play(
        self, player: "Player", field: "Field", target_position: Position, **kwargs
    ):
        return [
            CardPlayEvent(player=player, card=self),
            EnterFieldEvent(
                fighter=self.fighter, field=field, position=target_position
            ),
        ]


class TrickCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trick_effect: Event = kwargs.get("trick_effect", Event())

    def play(
        self, player: "Player", field: "Field", target_position: Position, **kwargs
    ):
        return [
            CardPlayEvent(player=player, card=self),
            self.trick_effect(
                player=player, field=field, target_position=target_position
            ),
        ]


class EnvironmentCard(Card):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.environment: Environment = kwargs.get("environment", Environment())

    def play(
        self, player: "Player", field: "Field", target_position: Position, **kwargs
    ):
        return [
            CardPlayEvent(player=player, card=self),
            SetEnvEvent(
                environment=self.environment,
                field=field,
                position=target_position,
            ),
        ]


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

        self.game: "Game" = kwargs.get("game", None)  # type: ignore quoted annotation

    def initial_draw(self) -> Event:
        cards = [self.deck.draw()] * 4
        super_power = self.hero.draw()
        cards.append(super_power)
        return [DrawEvent(player=self, card=card) for card in cards]

    def get_energy(self, amount: int) -> Event:
        return EnergyGainEvent(player=self, amount=amount)
