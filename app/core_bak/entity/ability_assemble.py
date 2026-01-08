from app.core_bak.entity.ability import Ability
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core_bak import Events


class DoubleStrike(Ability):
    def respond(self, event) -> Events:
        return []
