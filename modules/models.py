from dataclasses import dataclass
from PyQt6 import QtWidgets


@dataclass
class CropPoint:
    x: int
    y: int
    point: QtWidgets.QGraphicsEllipseItem

@dataclass
class Box:
    name: str
    x1: int
    y1: int
    x2: int
    y2: int
