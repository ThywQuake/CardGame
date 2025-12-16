from app.core.entity import Player, Field
from app.core.event import EventManager, ActionManager
from app.core.base import Faction, GamePhase
from app.core import Events
from queue import Queue


class Game:
    def __init__(self, **kwargs):
        self.zombie_player: Player = kwargs.get(
            "zombie_player", Player(faction=Faction.ZOMBIE)
        )
        self.plant_player: Player = kwargs.get(
            "plant_player", Player(faction=Faction.PLANT)
        )
        self.field = Field()
        self.event_manager = EventManager(game=self)
        self.input_queue: Queue = Queue()

        self.action_manager = ActionManager(game=self)

        # Status tracking
        self.current_player: Player = self.zombie_player
        self.turn_count: int = 1
        self.is_running: bool = False
        self.phase: GamePhase = GamePhase.INITIAL_DRAW
        self.surprise_phase: bool = False

    def start_game(self):
        self.is_running = True
        self.initial_draw()
        self.start_new_turn()

    def step(self, *args: Events):
        for events in args:
            self.event_manager.put_events(events)
        self.event_manager.notify(self)

    def act_on(self, action_payload: dict):
        """
        This is the only external method to accept player actions.
        """
        if not self.is_running:
            return

        self.action_manager.receive_network_input(action_payload)

    def tick(self, dt: float):
        """
        The main game loop tick function.
        Should be called periodically to advance the game state.
        """
        if not self.is_running:
            return

        # 1. Update ActionManager to process any active actions
        self.action_manager.update(dt)

    def start_new_turn(self):
        from app.core.event.event_assemble import TurnStartEvent

        self.turn_count += 1
        self.phase = GamePhase.TURN_START

        self.step([TurnStartEvent()])

        self.zombie_phase()

    def initial_draw(self):
        """Handle the initial card draw phase for both players."""
        from app.core.event.event_assemble import TurnStartEvent

        self.step(
            self.zombie_player.draw(4),
            self.plant_player.draw(4),
            self.zombie_player.get_energy(1),
            self.plant_player.get_energy(1),
            [TurnStartEvent()],
        )

    def zombie_phase(self):
        pass

    def plant_phase(self):
        pass

    def zombie_trick_phase(self):
        pass

    def combat_phase(self):
        pass

    def turn_end(self):
        pass

    def phase_end(self) -> Events:
        from app.core.event.event_assemble import (
            ZombiePhaseEndEvent,
            PlantPhaseEndEvent,
            ZombieTrickPhaseEndEvent,
            SurprisePhaseEndEvent,
        )

        match self.phase:
            case GamePhase.ZOMBIE_PHASE:
                return [ZombiePhaseEndEvent()]
            case GamePhase.PLANT_PHASE:
                return [PlantPhaseEndEvent()]
            case GamePhase.ZOMBIE_TRICK_PHASE:
                return [ZombieTrickPhaseEndEvent()]
            case _:
                if self.surprise_phase:
                    return [SurprisePhaseEndEvent()]
                return []
