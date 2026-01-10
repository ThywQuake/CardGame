from app.core.engine.player import Player
from app.core.base import Faction, GamePhase
from app.core.item.item_manager import ItemManager
from app.core.event.event_manager import EventManager
from app.core.action.action_manager import ActionManager
from app.core.event.events import (
    ZombiePhaseStartingEvent,
    ZombiePhaseEndingEvent,
    PlantPhaseStartingEvent,
    PlantPhaseEndingEvent,
    ZombieTrickPhaseStartingEvent,
    ZombieTrickPhaseEndingEvent,
)

from app.core.engine.combat import Combat

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, Any, Optional
    from app.core.event.event import Events


class Game:
    def __init__(self):
        # 1. Core manager initialization
        self.item_manager = ItemManager()
        self.event_manager = EventManager()
        self.action_manager = ActionManager()

        # 2. Player initialization
        self.zombie_player = Player(Faction.ZOMBIE, "Dr. Zomboss")
        self.plant_player = Player(Faction.PLANT, "Crazy Dave")
        self._player_map = {
            self.zombie_player.id: self.zombie_player,
            self.plant_player.id: self.plant_player,
        }

        # 3. Game state initialization
        self.phase: GamePhase = GamePhase.IDLE
        self.turn_count: int = 0
        self.is_running: bool = False

        # 4. Phase transition mapping (State Machine Definition)
        self._phase_cycle = {
            GamePhase.TURN_START: GamePhase.ZOMBIE_PHASE,
            GamePhase.ZOMBIE_PHASE: GamePhase.PLANT_PHASE,
            GamePhase.PLANT_PHASE: GamePhase.ZOMBIE_TRICK_PHASE,
            GamePhase.ZOMBIE_TRICK_PHASE: GamePhase.COMBAT_PHASE,
            GamePhase.COMBAT_PHASE: GamePhase.TURN_END,
            GamePhase.TURN_END: GamePhase.TURN_START,
        }

    def set_up(self, **kwargs):
        """
        Pre-game setup: Configure players, decks, heroes, etc.
        """
        pass  # Placeholder for future implementation

    def start_game(self):
        """
        Initialize the game board and enter the first turn.
        """
        if self.is_running:
            return

        print("🟢 Game Engine Starting...")

        # 1. Set up the board (Lanes, Positions)
        self.item_manager.set_up_board()

        # 2. Mark game as started
        self.is_running = True
        self.turn_count = 1

        # 3. Trigger the initial phase
        self.phase = GamePhase.TURN_START
        self._on_phase_start(self.phase)

    def tick(self, dt: float):
        """
        Heartbeat function: Called every frame to drive game logic.
        """
        if not self.is_running:
            return

        # 1. Update action manager (handles delays, animations, input waiting)
        self.action_manager.update(dt, self)

        # 2. Process event queue (handles chain reactions, damage resolution)
        # EventManager.notify loops until all events are processed
        self.event_manager.notify(self)

    def act_on(self, payload: Dict[str, Any]):
        """
        Process player commands from frontend/client.
        """
        if not self.is_running:
            return {"error": "Game not started"}

        # 1. Simple authorization and data unpacking
        # In a real project, payload should contain player_id to verify operation permission
        # Here we assume payload structure is already normalized by ActionManager

        # 2. Forward the action to ActionManager
        # ActionManager decides if the action is currently allowed (e.g., if waiting for input)
        success = self.action_manager.receive(payload, self)

        if not success:
            print(f"⚠️ Action rejected: {payload.get('operation_name', 'Unknown')}")

    def next_phase(self):
        """
        Advance the game to the next phase.
        """
        current = self.phase
        next_p = self._phase_cycle.get(current)

        if not next_p:
            print(f"❌ No next phase defined for {current}")
            return

        print(f"🔄 Phase Transition: {current.name} -> {next_p.name}")

        self._on_phase_end(current)
        self.phase = next_p

        # Special handling: Increment turn counter
        if next_p == GamePhase.TURN_START:
            self.turn_count += 1
            print(f"📅 Turn {self.turn_count} Begins")

        self._on_phase_start(next_p)

    def run_events(self, events: Events):
        """
        Interface to inject generated events into the system.
        """
        for event in events:
            if event:
                self.event_manager.event_queue.put(event)

    # --- Private helper methods (Logic Implementation) ---

    def _on_phase_start(self, phase: GamePhase):
        """Hook logic executed when a phase starts."""

        # 1. Activate/Freeze operation permissions for the corresponding faction
        if phase == GamePhase.ZOMBIE_PHASE:
            self.run_events([ZombiePhaseStartingEvent()])
        elif phase == GamePhase.PLANT_PHASE:
            self.run_events([PlantPhaseStartingEvent()])
        elif phase == GamePhase.ZOMBIE_TRICK_PHASE:
            self.run_events([ZombieTrickPhaseStartingEvent()])
        else:
            # Combat or resolution phases, disable all buttons
            self.item_manager.end_phase_button.deactivate()

        # 2. Trigger phase events (for Listener response, e.g., "draw cards at turn start")
        # self.event_manager.event_queue.put(PhaseStartEvent(phase=phase))

        # 3. Special handling for combat phase
        if phase == GamePhase.COMBAT_PHASE:
            self._resolve_combat()

    def _on_phase_end(self, phase: GamePhase):
        """Hook logic executed when a phase ends."""
        pass

    def _resolve_combat(self):
        """
        Initiate combat resolution process.
        Recommendation: Create a CombatAction and push it onto the ActionManager stack,
        rather than resolving directly here, so the frontend can play combat animations.
        """
        print("⚔️ Combat Logic Triggered (Placeholder)")
        # Example:
        combat = Combat(self)
        combat.resolve()

        self.next_phase()  # Automatically proceed to next phase after combat
