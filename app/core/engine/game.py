from app.core.entity import Player, Field
from app.core.event import EventManager
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

        # Status tracking
        self.current_player: Player = self.zombie_player
        self.turn_count: int = 1
        self.phase: GamePhase = GamePhase.INITIAL_DRAW
        self.surprise_phase: bool = False

    def step(self, *args: Events):
        for events in args:
            self.event_manager.put_events(events)
        self.event_manager.notify(self)

    def act_on(self, action_payload: dict):
        """Process an action payload from a player."""
        # Implementation of action processing goes here
        pass

    def run(self):
        self.initial_draw()
        while self.run_turn():
            pass

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

    def run_turn(self) -> bool:
        try:
            if self.turn_count > 1:
                self.turn_start()
            self.zombie_phase()
            self.plant_phase()
            self.zombie_trick_phase()
            self.combat_phase()
            self.turn_end()
            return True
        except Exception as e:
            print(e)
            return False

    def turn_start(self):
        from app.core.event.event_assemble import TurnStartEvent

        self.turn_count += 1
        self.step([TurnStartEvent()])

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
