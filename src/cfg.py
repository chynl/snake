import os

from src.cell import CellType
from src.direc import Direction
from src.pos import Pos


class Config:
    FPS: float = 60

    SCREEN_SIZE: tuple[float, float] = (330, 330)
    GRID_SIZE: int = 6
    CELL_SIZE: float = SCREEN_SIZE[0] / GRID_SIZE
    CELL_PADDING: float = 12

    INIT_SNAKE_DIREC: Direction = Direction.RIGHT
    INIT_SNAKE_FOOD: Pos = Pos(4, 4)

    INIT_SNAKE_POS: list[Pos] = [
        Pos(1, 1),
        Pos(1, 2),
        Pos(1, 3),
    ]

    INIT_SNAKE_CELLS: list[CellType] = [
        CellType.BODY_HORZ,
        CellType.BODY_HORZ,
        CellType.HEAD_RIGHT,
    ]

    LOG_DIR: str = os.path.join(".", "logs")
    LOG_PFX: str = "SNAKE"
    STATES_EXT: str = ".txt"
    RECORD_EXT: str = ".gif"
