from app.core.item.item import Item
from app.core.base import HeroConfig


class Hero(Item):
    def __init__(self, hero_config: HeroConfig, **kwargs):
        super().__init__(**kwargs)
        self.type = "Hero"

        for key, value in hero_config.__dict__.items():
            if value is not None:
                setattr(self, key, value)
