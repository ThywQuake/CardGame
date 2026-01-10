from app.core.action.action import Action, Operation

from typing import TYPE_CHECKING

from app.core.base import Faction
from app.core.engine.game import Game

if TYPE_CHECKING:
    from app.core.engine.game import Game
    from app.core.item.card import Card
    from app.core.item.position import Pos
    from app.core.item.target import Fighter


class PlayCardAction(Action):
    def __init__(self, faction: Faction, **kwargs):
        super().__init__(faction, **kwargs)
        self.lifetime = "persistent"

    def validate(self, operation: Operation, game: Game) -> bool:
        try:
            if operation.operation_name != "play_card":
                return False
            card_id = operation.data["card_id"]
            card = game.item_manager.get_by_id(card_id)  # type: ignore
            if card is None or card.type != "Card":
                return False

            card: Card
            if card.faction != self.faction or not card.activated[self.faction]:
                return False

            pos_id = operation.data["pos_id"]
            pos = game.item_manager.get_by_id(pos_id)  # type: ignore
            if pos is None or pos.type != "Pos":
                return False

            pos: Pos
            if pos.faction != self.faction:
                return False

            if pos.occupied:
                if self.faction == Faction.ZOMBIE:
                    return False
                slpos = game.item_manager.same_lane_pos(pos)
                if slpos is None or slpos.occupied:
                    return False
                stacker: Fighter = game.item_manager.get_by_id(pos.occupier_id)  # type: ignore
                if "team_up" in card.abilities or "team_up" in stacker.abilities:
                    return True

                return False
            else:
                return True

        except (KeyError, TypeError):
            return False
