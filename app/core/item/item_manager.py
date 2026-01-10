"""
An item manager is responsible for managing all items in the game.
It keeps track of items, their states, and provides methods to interact with them.
It connects the frontend to provide data for UI rendering and the backend to handle game logic.
It should be able to add, remove, update, and query items efficiently, the key is item's id.
"""

from .item import Item

# from .card import Card
from .end_phase import EndPhaseButton
from .hero import Hero
from .target import Fighter, Env
from .position import Pos, Lane, Board

from app.core.base import Faction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal, TypeVar, List, Tuple, Dict, Set, Optional
    from app.core.event.event import Event

    Items = TypeVar("Items", bound=Item)
    PositionTuple = Tuple[int, int, Faction]
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
        "end_phase_button",
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

        self._all_items: Dict[str, Items] = {}  # type: ignore
        self._indices: Dict[Range, Set[str]] = {
            "z_poses": set(),
            "p_poses": set(),
            "lanes": set(),
            "board": set(),
            "z_hero": set(),
            "p_hero": set(),
            "z_deck": set(),
            "z_hand": set(),
            "z_graveyard": set(),
            "p_deck": set(),
            "p_hand": set(),
            "p_graveyard": set(),
            "targets": set(),
            "end_phase_button": set(),
        }
        self._reverse_index: Dict[str, Range] = {}
        self.position_keeper: Dict[PositionTuple, str] = {}

    def keep_track(self, indice: Range, *items: Item):
        """
        Keep track of an item's group for easier management.
        """
        for item in items:
            self._all_items[item.id] = item
            self._indices[indice].add(item.id)
            self._reverse_index[item.id] = indice

    def add_item(self, item: Item, range: Range):
        """
        Add an item to the manager under the specified range.
        """
        items_dict: Dict[str, Item] = getattr(self, range)
        items_dict[item.id] = item
        self.keep_track(range, item)

    def get_position(self, position_tuple: PositionTuple) -> Pos | Lane | None:
        """
        Query a position or lane by its unique position tuple.
        """
        item_id = self.position_keeper.get(position_tuple, None)
        if item_id is None:
            return None
        item = self.get_by_id(item_id)
        if isinstance(item, (Pos, Lane)):
            return item
        return None

    def get_lane(self, lane_index: int) -> Lane | None:
        """
        Get a lane by its index.
        """
        lane_id = self.position_keeper.get((lane_index, 0, Faction.NEUTRAL), None)
        if lane_id is None:
            return None
        lane = self.get_by_id(lane_id)
        if isinstance(lane, Lane):
            return lane
        return None

    @property
    def poses(self) -> Dict[str, Pos]:
        """
        Get all positions managed by the item manager.
        """
        return merge_dicts([self._indices["z_poses"], self._indices["p_poses"]])

    @property
    def lanes(self) -> Dict[str, Lane]:
        """
        Get all lanes managed by the item manager.
        """
        lane_ids = self._indices["lanes"]
        lanes = {}
        for lane_id in lane_ids:
            lane = self.get_by_id(lane_id)
            if isinstance(lane, Lane):
                lanes[lane_id] = lane
        return lanes

    @property
    def num_lanes(self) -> int:
        """
        Get the number of lanes in the game.
        """
        return len(self._indices["lanes"])

    @property
    def end_phase_button(self) -> EndPhaseButton:
        """
        Get the end phase button item.
        """
        button_ids = self._indices["end_phase_button"]
        if len(button_ids) == 0:
            raise ValueError("End Phase Button not found in Item Manager.")
        button_id = next(iter(button_ids))
        button = self.get_by_id(button_id)
        if isinstance(button, EndPhaseButton):
            return button
        else:
            raise TypeError("Item with end_phase_button ID is not an EndPhaseButton.")

    def set_up_board(self):
        """
        Set up the board with initial positions and lanes.
        """

        end_phase_button = EndPhaseButton()
        self.add_item(end_phase_button, "end_phase_button")

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
            self.position_keeper[(i, 0, Faction.NEUTRAL)] = lane.id

            lanes.append(lane)

        board = Board(lanes)
        self.add_item(board, "board")

    def get_by_id(self, item_id: str) -> Optional[Item]:
        """
        Query an item by its unique ID.
        """

        if item_id in self._all_items:
            return self._all_items[item_id]
        return None

    def filter(
        self, func: Callable[[Items], bool], range: List[Range] | None = None
    ) -> List[Items]:
        """
        Filter items based on a provided function.
        """
        target_ids = set()
        if range is None:
            target_ids = set(self._all_items.keys())
        else:
            for r in range:
                target_ids.update(self._indices[r])

        return [
            self._all_items[item_id]
            for item_id in target_ids
            if func(self._all_items[item_id])  # type: ignore
        ]  # type: ignore

    def activate(self, items: List[Item], faction: Faction):
        """
        Activate a List of items for a specific faction.
        """
        for item in items:
            item.activate(faction)

    def deactivate(self, items: List[Item], faction: Faction | None = None):
        """
        Deactivate a List of items for a specific faction or all factions.
        """
        for item in items:
            item.deactivate(faction)

    def remove_item(self, item_id: str):
        """
        Remove an item from the manager by its ID.
        """
        item = self.get_by_id(item_id)
        if item is None:
            return

        indice = self._reverse_index.get(item_id, None)
        if indice is not None:
            if item_id in self._indices[indice]:
                self._indices[indice].remove(item_id)
            del self._reverse_index[item_id]
            del self._all_items[item_id]

    def opposite_poses(self, pos: Pos) -> List[Pos] | None:
        lane = self.get_lane(pos.lane)
        if lane is None:
            return None

        return lane.get_poses(pos.faction.opponent)

    def first_attackable_item(self, fighter: Fighter) -> Fighter | Hero | None:
        """
        Get the first attackable item in front of the fighter.
        """
        pos = fighter.on_pos
        if pos is None:
            return None

        lane = self.get_lane(pos.lane)
        if lane is None:
            return None
        if lane.is_empty(pos.faction.opponent):
            # No fighters in front, attack hero
            hero_id = (
                self._indices["p_hero"]
                if pos.faction == Faction.ZOMBIE
                else self._indices["z_hero"]
            )
            hero: Hero = self.get_by_id(list(hero_id)[0])  # type: ignore
            return hero

        frontier_pos = lane.get_frontier_pos(pos.faction.opponent)
        if frontier_pos is None:
            return None
        else:
            occupier_id = frontier_pos.occupier_id
            if occupier_id is None:
                return None
            target = self.get_by_id(occupier_id)
            if isinstance(target, Fighter):
                return target
            else:
                return None

    def same_lane_pos(self, pos: Pos) -> Pos | None:
        if pos.faction == Faction.ZOMBIE:
            return None

        res = self.get_position((pos.lane, 3 - pos.index, pos.faction))
        if res is None or not isinstance(res, Pos):
            return None

        return res

    def land_fighter(self, fighter: Fighter, pos: Pos):
        """
        Land a fighter on a specified position.
        """
        if pos.occupied and pos.faction == Faction.PLANT:
            former_fighter_id: str = pos.occupier_id  # type: ignore
            samelane_pos = self.same_lane_pos(pos)
            if samelane_pos is not None and not samelane_pos.occupied:
                former_fighter = self.get_by_id(former_fighter_id)
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

    def check_event_possible(self, event: Event) -> bool:
        """
        Check if an event is possible in the current game state.
        """
        source_id = event.source_id
        target_id = event.target_id

        flag1 = (source_id is None) or (source_id in self._indices)
        flag2 = (target_id is None) or (target_id in self._indices)
        return flag1 and flag2

    def get_lane_targets(self, lane_idx: int):
        lane = self.get_lane(lane_idx)
        env_id = lane.coverer_id if lane else None
        env = self.get_by_id(env_id) if env_id else None

        zombies_id = lane.get_fighters(Faction.ZOMBIE) if lane else []
        plants_id = lane.get_fighters(Faction.PLANT) if lane else []

        zombies = [self.get_by_id(z_id) for z_id in zombies_id]
        plants = [self.get_by_id(p_id) for p_id in plants_id]

        return {
            "env": env,
            "zombies": zombies,
            "plants": plants,
        }


if __name__ == "__main__":
    item_manager = ItemManager()
    item_manager.set_up_board()

    def func(pos: Pos) -> bool:
        return pos.faction == Faction.PLANT

    plant_poses = item_manager.filter(func, range=["p_poses", "z_poses"])
    item_manager.add_item(EndPhaseButton(), "all_items")
