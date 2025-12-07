from app.core.base import *
from app.core.models import *


class Action(ABC):
    def __init__(self, **kwargs):
        pass


class PlayCardAction(Action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card: Card = kwargs.get("card", None)
        self.target_position: Position = kwargs.get("target_position", Position())


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

    def run(self):
        self._inital_draw()
        try:
            while not self.game_state.END:
                self._zombie_phase()
                self._plant_phase()
                self._zombie_trick_phase()
                self._combat_phase()
                self._turn_end()
                self._turn_start()
        except GameEndingException as e:
            print(f"Game ended! Winner: {e.winner}")

    def _notify(self, event: Event):
        self.event_manager.notify(event)

    def _inital_draw(self):
        self.game_state.PHASE = GamePhase.INITIAL_DRAW
        self._notify(self.zombie_player.initial_draw())
        self._notify(self.plant_player.initial_draw())
        self._notify(self.zombie_player.get_energy(1))
        self._notify(self.plant_player.get_energy(1))

    def _listen(self, action: Action):
        if isinstance(action, PlayCardAction):
            self._notify(self.field.play_card(action.card, action.target_position))

    def _zombie_phase(self):
        pass

    def _plant_phase(self):
        pass

    def _zombie_trick_phase(self):
        pass

    def _combat_phase(self):
        pass

    def _turn_end(self):
        pass

    def _turn_start(self):
        pass
