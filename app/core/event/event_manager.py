from app.core.event.event import Event, Events
from app.core.event.listener import Listener
from queue import Queue

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.engine.game import Game
    from typing import List, Dict


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


class ListenerPool:
    def __init__(self):
        self.listeners: List[Listener] = []
        self.source_map: Dict[str | None, List[Listener]] = {None: []}
        self.on_event_group: Dict[str, List[Listener]] = {}

    def register(self, listener: Listener):
        self.listeners.append(listener)
        if listener.source is None:
            self.source_map[None].append(listener)
        else:
            sid = listener.source.id
            if sid not in self.source_map:
                self.source_map[sid] = []
            self.source_map[sid].append(listener)

        on_events = listener.on_events
        for event_name in on_events:
            if event_name not in self.on_event_group:
                self.on_event_group[event_name] = []
            self.on_event_group[event_name].append(listener)

    def unregister(self, listener: Listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

        if listener.source is None:
            if listener in self.source_map[None]:
                self.source_map[None].remove(listener)
        else:
            sid = listener.source.id
            if sid in self.source_map and listener in self.source_map[sid]:
                self.source_map[sid].remove(listener)

        on_events = listener.on_events
        for event_name in on_events:
            if (
                event_name in self.on_event_group
                and listener in self.on_event_group[event_name]
            ):
                self.on_event_group[event_name].remove(listener)

    def query_by_source(self, source_id: str | None) -> List[Listener]:
        return self.source_map.get(source_id, [])

    def query_by_event(self, event_name: str) -> List[Listener]:
        listeners = self.on_event_group.get(event_name, [])
        listeners.sort(key=lambda listener: listener.pos)
        return listeners


class EventManager:
    def __init__(self):
        self.listener_pool: ListenerPool = ListenerPool()
        self.event_queue: EventQueue = EventQueue(levels=8)

        self.MAX_STEPS = 1000  # Prevent infinite loops

    def register(self, listener: Listener):
        self.listener_pool.register(listener)

    def unregister(self, listener: Listener):
        self.listener_pool.unregister(listener)

    def notify(self, game: Game):
        temp_steps = 0
        while len(self.event_queue) > 0 and temp_steps < self.MAX_STEPS:
            current_event = self.event_queue.get()
            if current_event is None or (
                not game.item_manager.check_event_possible(current_event)
            ):
                continue

            temp_sequence: Events = []
            listeners = self.listener_pool.query_by_event(current_event.name)
            for listener in listeners:
                if not listener.validate(game):
                    continue
                response = listener.handle(current_event, game)
                temp_sequence.extend(response)
                if listener.end:
                    self.unregister(listener)
            for event in temp_sequence:
                if event is not None:
                    self.event_queue.put(event)
            temp_steps += 1
