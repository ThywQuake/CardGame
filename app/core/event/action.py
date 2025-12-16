from typing import TYPE_CHECKING, List, Optional
from abc import abstractmethod, ABC
from app.core.base import Position

if TYPE_CHECKING:
    from app.core import Events
    from app.core.engine.game import Game


class Action(ABC):
    """
    Base class for all actions.
    Designed to be non-blocking and updated per tick/frame.
    """

    def __init__(self, source=None, target=None, max_time=20.0, **kwargs):
        self.source = source
        self.target = target
        self.max_time = max_time

        self.elapsed_time: float = 0.0
        self.is_finished: bool = False

        # Buffer to store raw input data from network/UI asynchronously.
        # We use a List instead of Queue for thread-safety simplicity in single-threaded loops.
        self.input_data_buffer: List[dict] = []

    @abstractmethod
    def parse(self, raw_json: dict) -> Optional[Events]:
        """
        Parses raw dictionary data into a game Event.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def validate(self, raw_json: dict) -> bool:
        """
        Validates whether the action can be performed with given parameters.
        Must be implemented by subclasses.
        """
        pass

    def update(self, dt: float) -> Events:
        """
        Called once per frame/tick by the ActionManager.

        :param dt: Delta time (seconds) since the last frame.
        :return: A list of Events generated during this tick.
        """
        generated_events = []

        # 1. Handle Timeout Logic
        self.elapsed_time += dt
        if self.elapsed_time >= self.max_time:
            from app.core.event.event_assemble import ActionExpireEvent

            self.is_finished = True
            return [ActionExpireEvent()]

        # 2. Process Buffered Inputs
        # Consumes data pushed by receive_input()
        while self.input_data_buffer:
            data = self.input_data_buffer.pop(0)
            if self.validate(data):
                events = self.parse(data)
                if events:
                    generated_events.extend(events)
                    # Usually, if valid input is parsed, the action is considered complete.
                # You can set self.is_finished = True here depending on logic.

        return generated_events

    def receive_input(self, data: dict):
        """
        Public API to inject data into this action from external systems.
        """
        self.input_data_buffer.append(data)


class PlayCardAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_id: int = kwargs.get("card_id", -1)


class EndPhaseAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ending_phase: bool = True


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

    def push_action(self, action: Action):
        """Pushes a new action onto the stack, pausing the previous one."""
        self.stack.append(action)

    def receive_network_input(self, raw_json: dict):
        """
        The entry point for network payloads.
        Routes data to the active (top-most) action.
        """
        if not self.stack:
            return

        # Pass data to the current active action
        current_action = self.stack[-1]
        current_action.receive_input(raw_json)

    def update(self, dt: float):
        """
        Drives the action logic. Should be called by the main Game Loop.
        """
        if not self.stack:
            return

        current_action = self.stack[-1]

        # 1. Update the current action and collect generated events
        events_list = current_action.update(dt)

        # 2. Process generated events via the Game's central step method
        for events in events_list:
            self._handle_events(current_action, events)

    def _handle_events(self, action: Action, events):
        """
        Internal handler to manage control flow based on events.
        """
        from app.core.event.event_assemble import PhaseEndEvent, ActionExpireEvent

        # Handle Action Lifecycle Events
        if isinstance(events, ActionExpireEvent):
            if action in self.stack:
                self.stack.remove(action)
            self.game.step([events])
            return

        # Handle Phase Transitions (e.g., Player clicked "End Turn")
        if isinstance(events, PhaseEndEvent):
            # Clear stack as the phase is changing
            self.stack.clear()
            self.game.step([events])
            return

        # Forward normal gameplay events to the Game engine
        self.game.step([events])
