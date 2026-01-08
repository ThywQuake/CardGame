from app.core.item.item import Item
from app.core.event.events import EndPhaseEvent


class EndPhaseButton(Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "EndPhaseButton"

    def press(self) -> EndPhaseEvent:
        return EndPhaseEvent()
