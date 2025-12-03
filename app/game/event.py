from abc import ABC, abstractmethod
from queue import Queue
from app.game.base import *


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

    def notify(self, event: Event):
        self.event_queue.put(event)
        while not self.event_queue.empty():
            current_event = self.event_queue.get()
            for listener in self.listeners:
                if type(current_event) in listener.interested_events:
                    response = listener.react(current_event)
                    if response is not None:
                        self.event_queue.put(response)
                    if current_event.canceled:
                        break
