from abc import ABC, abstractmethod
from app.core.config import FighterCardConfig, EnvCardConfig, TrickCardConfig

class Card(ABC):
    def __init__(self, **kwargs):
        pass
    
    @abstractmethod
    def play(self):
        pass
    
    
class FighterCard(Card):
    def __init__(self, fighter_config: FighterCardConfig, **kwargs):
        super().__init__(**kwargs)
        self.fighter_config = fighter_config

        
class TrickCard(Card):
    def __init__(self, trick_config: TrickCardConfig, **kwargs):
        super().__init__(**kwargs)
        self.trick_config = trick_config
        
    
class EnvCard(Card):
    def __init__(self, env_config: EnvCardConfig, **kwargs):
        super().__init__(**kwargs)
        self.env_config = env_config