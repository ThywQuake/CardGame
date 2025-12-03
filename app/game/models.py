from abc import ABC, abstractmethod
from app.game.base import *


class Fighter(ABC):
    def __init__(self, fighter_config: FighterConfig):
        self.config = fighter_config
