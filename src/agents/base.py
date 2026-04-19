from typing import Protocol

from src.direc import Direction
from src.snake import Snake


class Agent(Protocol):
    def next_direc(self, snake: Snake) -> Direction: ...
