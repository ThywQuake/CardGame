from app.core.event.event import Event
from app.core.base import Lifetime
from app.core.event.listener import Listener
from typing import TYPE_CHECKING, List
from queue import Queue

if TYPE_CHECKING:
    from app.core import Events
from app.core.engine.game import Game


class EventManager:
    def __init__(self, **kwargs):
        self.listeners: List[Listener] = []
        self.event_queue: Queue[Event] = Queue()

    def register(self, listener: Listener):
        self.listeners.append(listener)
        self.listeners.sort(key=lambda listener: listener.position)

    def notify(self, event: Event, game: Game):
        self.event_queue.put(event)

        while self.event_queue.qsize() > 0:
            current_event = self.event_queue.get()
            self._check_event(current_event)
            temp_sequence: Events = []
            for listener in self.listeners:
                if not self.validate_listener(listener):
                    continue
                response = listener.handle(current_event, game)
                if current_event.cancelled:
                    temp_sequence: Events = []
                    break
                temp_sequence = temp_sequence + response
            else:
                sequence = current_event.execute(game) + temp_sequence
                self._put_events(sequence)

            self.unregister()

    def _put_events(self, events: Events):
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

    def unregister(self):
        self.listeners = [listener for listener in self.listeners if not listener.end]
