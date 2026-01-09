from app.core.event.event_manager import EventManager
from app.core.item.item_manager import ItemManager
from app.core.action.action_manager import ActionManager
from app.core.event.event import Events


class Game:
    def __init__(self):
        self.event_manager = EventManager()
        self.item_manager = ItemManager()
        self.action_manager = ActionManager()

    def run_events(self, events: Events): ...
