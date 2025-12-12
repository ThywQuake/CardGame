from app.core.event.event import Event
from app.core.base import Lifetime
from app.core.event.listener import Listener
from typing import TYPE_CHECKING, List
from queue import Queue

if TYPE_CHECKING:
    from app.core import Events
from app.core.engine.game import Game


class EventQueue:
    def __init__(self, levels: int = 8):
        """
        Set up a multi-level priority queue for events.
        Higher priority events (lower numerical value) are processed first.

        :param levels: Number of priority levels.

        Event priority mapping:
        - level 0: Game Over Events + Surprise Phase Starting.
        - level 1: Critical Events (e.g., Hero Hurt)
        - level 2: High Priority Events (e.g., Card Draw, Energy Gain)
        - level 3: Normal Events (e.g., Card Play)
        - level 4: Pair Event: Surprise Phase Ending.
        - level 5: Pair Event: Lane Combat Starting/Ending.
        - level 6: Pair Event: Phase Starting/Ending.
        - level 7: Pair Event: Turn Starting/Ending.

        """
        self.levels = levels
        self.queues: List[Queue[Event]] = [Queue() for _ in range(levels)]

    def put(self, event: Event):
        priority = event.priority
        if priority < 0:
            priority = 0
        elif priority >= self.levels:
            priority = self.levels - 1
        self.queues[priority].put(event)

    def get(self) -> Event | None:
        for queue in self.queues:
            if not queue.empty():
                return queue.get()
        return None

    def __len__(self):
        return sum(queue.qsize() for queue in self.queues)


class EventManager:
    def __init__(self, **kwargs):
        self.listeners: List[Listener] = []
        self.event_queue: EventQueue = EventQueue(levels=5)

    def register(self, listener: Listener):
        self.listeners.append(listener)
        self.listeners.sort(key=lambda listener: listener.position)

    def notify(self, game: Game):
        while len(self.event_queue) > 0:
            current_event = self.event_queue.get()
            if current_event is None:
                break
            self._check_event(current_event)
            temp_sequence: Events = []
            for listener in tuple(self.listeners):
                if not self.validate_listener(listener):
                    continue
                response = listener.handle(current_event, game)
                if current_event.cancelled:
                    temp_sequence: Events = []
                    break
                temp_sequence = temp_sequence + response
            else:
                sequence = current_event.execute(game) + temp_sequence
                self.put_events(sequence)

            self.unregister()

    def put_events(self, events: Events):
        for event in events:
            if event is not None:
                self.event_queue.put(event)

    def _check_event(self, event: Event):
        source = event.source
        target = event.target
        if getattr(source, "in_graveyard", False) or getattr(
            target, "in_graveyard", False
        ):
            event.cancel()

    def _check_listener_ending(self, listener: Listener):
        match listener.lifetime:
            case Lifetime.ONCE:
                return listener.end
            case Lifetime.IN_DECK:
                return not getattr(listener.source, "in_deck", False)
            case Lifetime.IN_HAND:
                return not getattr(listener.source, "in_hand", False)
            case Lifetime.IN_FIELD:
                return not getattr(listener.source, "in_field", False)
            case Lifetime.PERMANENT:
                return False
        return True

    def validate_listener(self, listener: Listener):
        end = self._check_listener_ending(listener)
        if end:
            listener.end = True
        return not end

    def unregister(self, listener: Listener | None = None):
        if listener is not None:
            self.listeners = [lis for lis in self.listeners if lis != listener]
        else:
            self.listeners = [
                listener for listener in self.listeners if not listener.end
            ]
