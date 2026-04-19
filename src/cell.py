from enum import Enum, auto


class CellValue(Enum):
    EMPTY = 0
    FOOD = -1


class CellType(Enum):
    EMPTY = auto()
    FOOD = auto()
    HEAD_UP = auto()
    HEAD_LEFT = auto()
    HEAD_RIGHT = auto()
    HEAD_DOWN = auto()
    BODY_HORZ = auto()
    BODY_VERT = auto()
    BODY_TURN_UL = auto()
    BODY_TURN_UR = auto()
    BODY_TURN_DL = auto()
    BODY_TURN_DR = auto()


class CellColor(Enum):
    BACKGROUND = (33, 33, 33)
    GRID_LINE = (97, 97, 97)
    FOOD = (255, 245, 157)
    SNAKE_WALKING = (245, 245, 245)
    SNAKE_DEAD = (239, 83, 80)
    SNAKE_FULL = (163, 255, 88)
