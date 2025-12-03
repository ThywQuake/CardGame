from app.game.base import *
from app.game.models import *
from app.game.event import *


class Action(ABC):
    def __init__(self, **kwargs):
        pass


class PlayCardAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card: Card = kwargs.get("card", None)
        self.target_position: tuple[int, int] = kwargs.get("target_position", (0, 0))


class EndPhaseAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Game:
    def __init__(self, **kwargs):
        self.field: Field = Field(self)
        self.event_manager: EventManager = EventManager(game=self)
        self.zombie_player: Player = kwargs.get("zombie_player", Player())
        self.plant_player: Player = kwargs.get("plant_player", Player())
        self.game_state: GameState = GameState()

    def start(self):
        pass

    def apply_action(self, action: Action):
        pass
