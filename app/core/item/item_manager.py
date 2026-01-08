"""
An item manager is responsible for managing all items in the game.
It keeps track of items, their states, and provides methods to interact with them.
It connects the frontend to provide data for UI rendering and the backend to handle game logic.
It should be able to add, remove, update, and query items efficiently, the key is item's id.
"""

from .item import Item
from .card import Card
from .end_phase import EndPhaseButton
from .hero import Hero
from .target import Target, Fighter, Env
from .position import Pos, Lane, Board

from app.core.base import Faction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal, TypeVar

    Items = TypeVar("Items", bound=Item)

    Range = Literal[
        "all_items",
        "z_poses",
        "p_poses",
        "poses",
        "lanes",
        "board",
        "z_hero",
        "p_hero",
        "z_deck",
        "z_hand",
        "z_graveyard",
        "p_deck",
        "p_hand",
        "p_graveyard",
        "targets",
    ]


def merge_dicts(dicts):
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


class ItemManager:
    def __init__(self):
        """
        Initialize a manager of all operatable items in the game, by items' id.
        """
        self.z_poses: dict[str, Pos] = {}
        self.p_poses: dict[str, Pos] = {}
        self.lanes: dict[str, Lane] = {}
        self.board: dict[str, Board] = {}

        self.z_hero: dict[str, Hero] = {}
        self.p_hero: dict[str, Hero] = {}

        self.z_deck: dict[str, Card] = {}
        self.z_hand: dict[str, Card] = {}
        self.z_graveyard: dict[str, Card] = {}

        self.p_deck: dict[str, Card] = {}
        self.p_hand: dict[str, Card] = {}
        self.p_graveyard: dict[str, Card] = {}

        self.end_phase_button: EndPhaseButton = EndPhaseButton()

        self.targets: dict[str, Target] = {}

        self.group_keeper: dict[str, str] = {}
        self.position_keeper: dict[tuple, str] = {}

    def keep_track(self, group_name: str, *items: Item):
        """
        Keep track of an item's group for easier management.
        """
        for item in items:
            self.group_keeper[item.id] = group_name

    def add_item(self, item: Item, range: Range):
        """
        Add an item to the manager under the specified range.
        """
        items_dict: dict[str, Item] = getattr(self, range)
        items_dict[item.id] = item
        self.keep_track(range, item)

    def query_position(self, position_tuple: tuple) -> Pos | Lane | None:
        """
        Query a position or lane by its unique position tuple.
        """
        item_id = self.position_keeper.get(position_tuple, None)
        if item_id is None:
            return None
        group_name = self.group_keeper.get(item_id, None)
        if group_name is None:
            return None
        items_dict: dict[str, Pos | Lane] = getattr(self, group_name)  # type: ignore
        return items_dict.get(item_id, None)

    @property
    def poses(self) -> dict[str, Pos]:
        """
        Get all positions managed by the item manager.
        """
        return merge_dicts([self.z_poses, self.p_poses])

    @property
    def all_items(self) -> dict[str, Items]:  # type: ignore
        """
        Get all items managed by the item manager.
        """

        all_items = merge_dicts([
            self.poses,
            self.lanes,
            self.board,
            self.z_hero,
            self.p_hero,
            self.z_deck,
            self.z_hand,
            self.z_graveyard,
            self.p_deck,
            self.p_hand,
            self.p_graveyard,
            self.targets,
        ])
        all_items[self.end_phase_button.id] = self.end_phase_button
        return all_items

    def set_up_board(self):
        """
        Set up the board with initial positions and lanes.
        """

        lanes = []
        for i in range(5):
            z_pos = Pos(i, 1, Faction.ZOMBIE)
            p_pos1 = Pos(i, 1, Faction.PLANT)
            p_pos2 = Pos(i, 2, Faction.PLANT)

            self.add_item(z_pos, "z_poses")
            self.add_item(p_pos1, "p_poses")
            self.add_item(p_pos2, "p_poses")

            self.position_keeper[(i, 1, Faction.ZOMBIE)] = z_pos.id
            self.position_keeper[(i, 1, Faction.PLANT)] = p_pos1.id
            self.position_keeper[(i, 2, Faction.PLANT)] = p_pos2.id

            lane = Lane(i, [z_pos, p_pos1, p_pos2])
            self.add_item(lane, "lanes")
            self.position_keeper[(i,)] = lane.id

            lanes.append(lane)

        board = Board(lanes)
        self.add_item(board, "board")

    def query_by_id(self, item_id: str) -> Item | None:
        """
        Query an item by its unique ID.
        """
        group_name = self.group_keeper.get(item_id, None)
        if group_name is None:
            return None
        items_dict: dict[str, Items] = getattr(self, group_name)  # type: ignore
        return items_dict.get(item_id, None)

    def filter(
        self, func: Callable[[Items], bool], range: list[Range] | None = None
    ) -> list[Items]:
        """
        Filter items based on a provided function.
        """
        if range is None:
            range = ["all_items"]

        try:
            items_dict: dict[str, Items] = merge_dicts([
                getattr(self, r) for r in range
            ])
        except AttributeError:
            items_dict: dict[str, Items] = self.all_items

        return [item for item in items_dict.values() if func(item)]

    def activate(self, items: list[Item], faction: Faction):
        """
        Activate a list of items for a specific faction.
        """
        for item in items:
            item.activate(faction)

    def deactivate(self, items: list[Item], faction: Faction | None = None):
        """
        Deactivate a list of items for a specific faction or all factions.
        """
        for item in items:
            item.deactivate(faction)

    def remove_item(self, item_id: str):
        """
        Remove an item from the manager by its ID.
        """
        group_name = self.group_keeper.get(item_id, None)
        if group_name is None:
            return
        items_dict: dict[str, Item] = getattr(self, group_name)
        if item_id in items_dict:
            del items_dict[item_id]
            del self.group_keeper[item_id]

    def opposite_poses(self, pos: Pos) -> list[Pos] | None:
        lane = self.query_position((pos.lane,))
        if lane is None or not isinstance(lane, Lane):
            return None

        return lane.get_poses(pos.faction.opponent)

    def first_attackable_item(self, fighter: Fighter) -> Fighter | Hero | None:
        """
        Get the first attackable item in front of the fighter.
        """
        pos = fighter.on_pos
        if pos is None:
            return None

        lane = self.query_position((pos.lane,))
        if lane is None or not isinstance(lane, Lane):
            return None
        if lane.is_empty(pos.faction.opponent):
            # No fighters in front, attack hero
            hero_dict = self.p_hero if pos.faction == Faction.ZOMBIE else self.z_hero
            if len(hero_dict) == 0:
                return None
            return list(hero_dict.values())[0]

        frontier_pos = lane.get_frontier_pos(pos.faction.opponent)
        if frontier_pos is None:
            return None
        else:
            occupier_id = frontier_pos.occupier_id
            if occupier_id is None:
                return None
            target = self.query_by_id(occupier_id)
            if isinstance(target, Fighter):
                return target
            else:
                return None

    def samelane_pose(self, pos: Pos) -> Pos | None:
        if pos.faction == Faction.ZOMBIE:
            return None

        res = self.query_position((pos.lane, 3 - pos.index, pos.faction))
        if res is None or not isinstance(res, Pos):
            return None

        return res

    def land_fighter(self, fighter: Fighter, pos: Pos):
        """
        Land a fighter on a specified position.
        """
        if pos.occupied and pos.faction == Faction.PLANT:
            former_fighter_id: str = pos.occupier_id  # type: ignore
            samelane_pos = self.samelane_pose(pos)
            if samelane_pos is not None and not samelane_pos.occupied:
                former_fighter = self.query_by_id(former_fighter_id)
                if isinstance(former_fighter, Fighter):
                    former_fighter.move_to(samelane_pos)

        fighter.move_to(pos)
        self.add_item(fighter, "targets")

    def cover_env(self, env: Env, lane: Lane):
        """
        Cover a lane with an environment card.
        """
        lane.cover_by(env.id)
        env.on_lane = lane
        self.add_item(env, "targets")


if __name__ == "__main__":
    item_manager = ItemManager()
    item_manager.set_up_board()

    def func(pos: Pos) -> bool:
        return pos.faction == Faction.PLANT

    plant_poses = item_manager.filter(func, range=["p_poses", "z_poses"])
    item_manager.add_item(EndPhaseButton(), "all_items")
