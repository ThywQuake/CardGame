from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class State(ABC):
    INITIAL_COST: int = 0
    CURRENT_COST: int = 0
    MAX_COST: int = 0

    @abstractmethod
    def load(self, **kwargs):
        pass

    @abstractmethod
    def modify(self, **kwargs):
        pass


@dataclass
class FighterState(State):
    INITIAL_STRENGTH: int = 0
    CURRENT_STRENGTH: int = 0
    MAX_STRENGTH: int = 0

    INITIAL_HEALTH: int = 0
    CURRENT_HEALTH: int = 0
    MAX_HEALTH: int = 0

    IS_HURT: bool = False
    IS_DEAD: bool = False

    GROWN_COST: int = 0
    GROWN_STRENGTH: int = 0
    GROWN_HEALTH: int = 0

    # buffs
    FROZEN: bool = False
    DOOMED: bool = False

    def load(self, **kwargs):
        self.INITIAL_STRENGTH = self.CURRENT_STRENGTH = self.MAX_STRENGTH = kwargs.get(
            "strength", 0
        )
        self.INITIAL_HEALTH = self.CURRENT_HEALTH = self.MAX_HEALTH = kwargs.get(
            "health", 0
        )
        self.INITIAL_COST = self.CURRENT_COST = self.MAX_COST = kwargs.get("cost", 0)

    def take_damage(self, value: int):
        self.CURRENT_HEALTH -= value
        if self.CURRENT_HEALTH < self.MAX_HEALTH:
            self.IS_HURT = True
        if self.CURRENT_HEALTH <= 0:
            self.CURRENT_HEALTH = 0
            self.IS_DEAD = True

    def heal(self, value: int):
        self.CURRENT_HEALTH += value
        if self.CURRENT_HEALTH > self.MAX_HEALTH:
            self.CURRENT_HEALTH = self.MAX_HEALTH
            self.IS_HURT = False

    def modify(self, cost: int = 0, strength: int = 0, health: int = 0):
        self.GROWN_COST += cost
        self.GROWN_STRENGTH += strength
        self.GROWN_HEALTH += health

        self.MAX_COST += cost
        self.CURRENT_COST += cost

        self.MAX_STRENGTH += strength
        self.CURRENT_STRENGTH += strength

        self.MAX_HEALTH += health
        self.CURRENT_HEALTH += health


@dataclass
class EnvironmentState(State):
    def load(self, **kwargs):
        self.INITIAL_COST = self.CURRENT_COST = self.MAX_COST = kwargs.get("cost", 0)

    def modify(self, cost: int = 0):
        self.MAX_COST += cost
        self.CURRENT_COST += cost
