from app.core.base import Faction
from uuid import uuid4


class Player:
    """Simple player object for identity holding and authorization."""

    def __init__(self, faction: Faction, name: str = "Player"):
        self.id = str(uuid4())
        self.faction = faction
        self.name = name

        self.energy: int = 0  # Initialize player energy
