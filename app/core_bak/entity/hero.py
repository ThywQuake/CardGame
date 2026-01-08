from app.core_bak.config import HeroConfig
from app.core_bak.entity.slot import Deck


class Hero:
    def __init__(self, **kwargs):
        self.config: HeroConfig = kwargs.get("config", HeroConfig())
        self.super_powers: Deck = kwargs.get("super_powers", Deck())
