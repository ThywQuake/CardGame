"""
Never operate same-level class inside class itself, refer to higher-level management module instead.
e.g., do not query ajacent lane inside Lane class, refer to ItemManager instead.
"""

from app.core.item.item import Item
from app.core.base import Faction


class Pos(Item):
    def __init__(self, lane: int, index: int, faction: Faction, **kwargs):
        super().__init__(**kwargs)
        self.type = "Pos"

        self.lane: int = lane
        self.index: int = index
        self.faction: Faction = faction

        self.occupied: bool = False
        self.occupier_id: str | None = None

    def occupy_by(self, item_id: str):
        self.occupied = True
        self.occupier_id = item_id

    def vacate(self):
        self.occupied = False
        self.occupier_id = None


class Lane(Item):
    def __init__(
        self,
        lane: int,
        pos: list[Pos],
        coverable: bool = True,
        water: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.type = "Lane"

        self.lane = lane
        self.pos = pos
        # For most cases, pos arranged as [Zombie_Pos, Plant_Pos1, Plant_Pos2]

        self.coverable: bool = coverable
        self.covered: bool = False
        self.coverer_id: str | None = None

    def get_poses(self, faction: Faction | None = None) -> list[Pos]:
        match faction:
            case Faction.PLANT:
                # return [p for p in self.pos if p.faction == Faction.PLANT]
                return self.pos[1:]  # Assume pos[0] is always Zombie_Pos
            case Faction.ZOMBIE:
                # return [p for p in self.pos if p.faction == Faction.ZOMBIE]
                return [self.pos[0]]  # Assume pos[0] is always Zombie_Pos
            case _:
                return self.pos

    def get_fighters(self, faction: Faction) -> list[str]:
        poses = self.get_poses(faction)
        return [
            p.occupier_id for p in poses if p.occupied and p.occupier_id is not None
        ]

    def get_vacant_pos(self, faction: Faction) -> Pos | None:
        poses = self.get_poses(faction)
        for p in poses:
            if not p.occupied:
                return p
        return None

    def get_frontier_pos(self, faction: Faction) -> Pos | None:
        # Frontier pos is the first occupied pos in the lane for the faction
        poses = self.get_poses(faction)
        for p in poses:
            if p.occupied:
                return p
        return None

    def is_full(self, faction: Faction) -> bool:
        poses = self.get_poses(faction)
        return all(p.occupied for p in poses)

    def is_empty(self, faction: Faction) -> bool:
        poses = self.get_poses(faction)
        return all(not p.occupied for p in poses)

    def cover_by(self, item_id: str):
        if self.coverable:
            self.covered = True
            self.coverer_id = item_id

    def uncover(self):
        if self.coverable:
            self.covered = False
            self.coverer_id = None


class Board(Item):
    def __init__(self, lanes: list[Lane], **kwargs):
        super().__init__(**kwargs)
        self.type = "Board"

        self.lanes = lanes

    def get_lanes(self) -> list[Lane]:
        return self.lanes

    def get_frontier_pos(self, faction: Faction) -> list[Pos | None]:
        return [lane.get_frontier_pos(faction) for lane in self.lanes]

    def get_vacant_lanes(self, faction: Faction) -> list[Lane]:
        return [lane for lane in self.lanes if not lane.is_full(faction)]
