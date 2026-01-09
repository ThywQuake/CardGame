"""
An action is an operation that performed by a player during their turn.
All the actions are operating on items that are activated in the proper phase.
To translate an operation into event, we need to open an action, to wait for specific input from player.
When operating an action, new actions may be opened, so actions need to be managed in a stack structure.
Actions are non-blocking, they are updated per tick/frame until they are finished or timed out.
In a word, an action is a stateful handler that processes player inputs over time and generates game events accordingly.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.core.base import Faction

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.event import Events
    from app.core.item.item import Item
    from app.core.engine.game import Game
    from typing import Callable, List, Literal, Any, Dict


@dataclass
class Operation:
    operation_name: Literal["play_card", "select_target", "end_turn", "select_pos"]
    faction: Faction
    data: Dict[str, Any]


class Action(ABC):
    def __init__(self, faction: Faction, **kwargs):
        self.faction = faction
        self.restrictions: List[Callable[[Item], bool]] = kwargs.get("restrictions", [])
        self.max_time: float = kwargs.get("max_time", 20.0)
        self.lifetime: Literal["once", "persistent"] = kwargs.get("lifetime", "once")

        self.elapsed_time: float = 0.0
        self.is_finished: bool = False

        self.input_data_buffer: List[Operation] = []

    @abstractmethod
    def validate(self, operation: Operation, game: Game) -> bool:
        """
        Validates whether the action can be performed with given parameters.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def parse(self, operation: Operation, game: Game) -> Events:
        """
        Parses raw dictionary data into a game Event.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def default_events(self, game: Game) -> Events:
        """
        Generates the default event for this action.
        Must be implemented by subclasses.
        """
        pass

    def receive(self, operation: Operation):
        self.input_data_buffer.append(operation)

    def update(self, dt: float, game: Game) -> Events | None:
        """
        Called once per frame/tick by the ActionManager.

        :param dt: Delta time (seconds) since the last frame.
        :return: A list of Events generated during this tick.
        """
        self.elapsed_time += dt

        if self.input_data_buffer:
            operation = self.input_data_buffer.pop(0)
            if self.validate(operation, game):
                events = self.parse(operation, game)
                if self.lifetime == "once":
                    self.is_finished = True
                return events

        if self.elapsed_time >= self.max_time:
            self.is_finished = True
            return self.default_events(game)

        return None
