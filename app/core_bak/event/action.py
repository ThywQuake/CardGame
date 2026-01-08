from typing import TYPE_CHECKING, List, Optional, Callable
from abc import abstractmethod, ABC
from app.core_bak.base import Position

if TYPE_CHECKING:
    from app.core_bak import Events
    from app.core_bak.engine.game import Game
    from app.core_bak.entity import Player


class Action(ABC):
    """
    Base class for all actions.
    Designed to be non-blocking and updated per tick/frame.
    """

    def __init__(self, **kwargs):
        self.player = kwargs.get("player", None)
        self.restrictions: dict[str, Callable[[dict], bool]] = kwargs.get(
            "restrictions", {}
        )
        self.active_items: list = kwargs.get("active_items", [])
        self.max_time = kwargs.get("max_time", 20.0)

        self.elapsed_time: float = 0.0
        self.is_finished: bool = False

        self.input_data_buffer: List[dict] = []

    @abstractmethod
    def parse(self, action: dict) -> Optional[Events]:
        """
        Parses raw dictionary data into a game Event.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def validate(self, action: dict) -> bool:
        """
        Validates whether the action can be performed with given parameters.
        Must be implemented by subclasses.
        """
        pass

    @property
    @abstractmethod
    def default_events(self) -> Events:
        """
        Generates the default event for this action.
        Must be implemented by subclasses.
        """
        pass

    def update(self, dt: float) -> Optional[Events]:
        """
        Called once per frame/tick by the ActionManager.

        :param dt: Delta time (seconds) since the last frame.
        :return: A list of Events generated during this tick.
        """
        self.elapsed_time += dt
        if self.input_data_buffer:
            action_data = self.input_data_buffer.pop(0)
            if self.validate(action_data):
                events = self.parse(action_data)
                if events:
                    return events
        else:
            if self.elapsed_time >= self.max_time:
                self.is_finished = True
                return self.default_events

        return None

    def receive_input(self, data: dict):
        """
        Public API to inject data into this action from external systems.
        """
        self.input_data_buffer.append(data)


class PlayCardAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse(self, action: dict) -> Events:
        from app.core_bak.event.event_assemble import CardPlayEvent

        card_id = action["card_id"]
        position = action["position"]
        return [CardPlayEvent(player=self.player, card_id=card_id, position=position)]

    def validate(self, action: dict) -> bool:
        if action.get("type") != "play_card":
            return False
        if "card_id" not in action or "position" not in action:
            return False
        for res_func in self.restrictions.values():
            if not res_func(action):
                return False
        return True

    def default_events(self) -> Events:
        from app.core_bak.event.event_assemble import ActionExpireEvent

        return [ActionExpireEvent()]


class SelectTargetAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_id: int = kwargs.get("target_id", -1)


class SelectPositionAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position: Position = kwargs.get("position", Position())


class ActionManager:
    """
    Manages the lifecycle of Actions using a Stack architecture.
    """

    def __init__(self, game: Game):
        self.stack: List[Action] = []
        self.game: Game = game
        self.current_player: Optional["Player"] = None
        self.paused: bool = False  # External pause flag, if true, can't call update()

    def push_action(self, action: Action):
        """Pushes a new action onto the stack, pausing the previous one."""
        self.stack.append(action)
        self.game.activate(action.active_items)

    def receive_network_input(self, action: dict):
        """
        The entry point for network payloads.
        Routes data to the active (top-most) action.
        """
        if not self.stack:
            return

        # Pass data to the current active action
        current_action = self.stack[-1]

        # Abandon input when an action is fed
        self.temp_player = self.game.current_player
        self.current_player = None
        current_action.receive_input(action)

    def update(self, dt: float):
        """
        Drives the action logic. Should be called by the main Game Loop.
        While processing events, the clock wont tick.
        """
        if not self.stack:
            return

        current_action = self.stack[-1]

        # 1. Update the current action and collect generated events
        events = current_action.update(dt)
        if not events:
            return

        # 2. Process generated events via the Game's central step method
        self.paused = True
        self._handle_events(current_action, events)
        self.paused = False
        self.game.current_player = (
            self.temp_player
        )  # Restore current player after action processing

    def _handle_events(self, action: Action, events: Events):
        """
        Internal handler to manage control flow based on events.
        """
        from app.core_bak.event.event_assemble import PhaseEndEvent, ActionExpireEvent

        # Handle Action Lifecycle Events
        if isinstance(events, ActionExpireEvent):
            if action in self.stack:
                self.stack.remove(action)
            self.game.step(events)
            return

        # Handle Phase Transitions (e.g., Player clicked "End Turn")
        if isinstance(events, PhaseEndEvent):
            # Clear stack as the phase is changing
            self.stack.clear()
            self.game.step(events)
            return

        # Forward normal gameplay events to the Game engine
        self.game.step(events)
