"""
Provides combat mechanics and turn management for the game.
"""

from app.core.event.events import (
    LaneCombatStartingEvent,
    LaneCombatEndingEvent,
    CombatPhaseStartingEvent,
    CombatPhaseEndingEvent,
    AttackEvent,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.engine.game import Game
    from app.core.item.target import Fighter
    from app.core.event.events import Events


class Combat:
    def __init__(self, game: Game):
        self.game = game
        self.IM = game.item_manager

    def _resolve_lane_combat(self, lane_idx: int):
        """
        Resolves combat in a specific lane between plants and zombies.
        """
        # Placeholder for combat resolution logic
        self.game.run_events([LaneCombatStartingEvent(lane_idx)])

        targets = self.IM.get_lane_targets(lane_idx)
        zombies: list[Fighter] = targets["zombies"]
        plants: list[Fighter] = targets["plants"]
        attack_events: Events = []
        for z in zombies:
            aim = self.IM.first_attackable_item(z)
            if aim:
                attack_events.append(
                    AttackEvent(
                        attacker_id=z.id,
                        defender_id=aim.id,
                        damage=z.strength,
                    )
                )
        for p in plants:
            aim = self.IM.first_attackable_item(p)
            if aim:
                attack_events.append(
                    AttackEvent(
                        attacker_id=p.id,
                        defender_id=aim.id,
                        damage=p.strength,
                    )
                )
        self.game.run_events(attack_events)

        self.game.run_events([LaneCombatEndingEvent(lane_idx)])

    def resolve(self):
        """
        Resolves combat for all lanes during the combat phase.
        """

        self.game.run_events([CombatPhaseStartingEvent()])

        num_lanes = self.IM.num_lanes
        for lane_idx in range(num_lanes):
            self._resolve_lane_combat(lane_idx)

        self.game.run_events([CombatPhaseEndingEvent()])
