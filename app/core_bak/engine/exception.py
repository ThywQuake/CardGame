from app.core_bak.base import Faction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core_bak.entity.player import Player


class GameOverException(Exception):
    def __init__(self, winner: Faction):
        self.winner = winner
        super().__init__(f"Game ended! Winner: {self.winner}")


class SurprisePhaseException(Exception):
    def __init__(self, player: "Player"):
        self.player = player
        super().__init__(f"Surprise phase triggered for player: {self.player.name}")
