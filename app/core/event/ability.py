from abc import ABC, abstractmethod
from .listener import Listener

class Ability(ABC, Listener):
    