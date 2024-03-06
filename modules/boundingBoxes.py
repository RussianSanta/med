import os
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (QGraphicsTextItem, QInputDialog, QGraphicsRectItem, QInputDialog, QPushButton)
from modules.messages import get_msg_result
from modules.meta import (addMetaButton, addMetaComboBoxItems, removeMetaButtons)
import pickle

def get_rectangle(x1, y1, x2, y2) -> QGraphicsRectItem:
    """Создание и оформление рамки"""
    rect = QGraphicsRectItem(x1, y1, x2 - x1, y2 - y1)
    rect.setPen(QColor(0, 255, 0))
    rect.setBrush(QColor(0, 255, 0, 40))
    return rect

def get_rectangle_name(name: str, x, y) -> QGraphicsTextItem:
    """Оформление текста над рамкой"""
    text = QGraphicsTextItem(name)
    text.setFont(QFont("Helvetica", 12, QFont.Weight.Bold))
    text.setDefaultTextColor(QColor(255, 255, 255))
    text.setPos(x - 4, y - text.boundingRect().height() + 4)
    text.setHtml(f'<div style="background:#008700;">{name}</div>')
    return text

def get_name_item_by_text(self, text: str):
    """Получить текстовый объект из сцены по ее тексту"""
    for name_item in self.current_scene.items():
        if isinstance(name_item, QGraphicsTextItem) and name_item.toPlainText() == text:
            return name_item

def get_box_by_top_left(self, top_left: int):
    """Получение нужной рамки по верхнему краю"""
    for box in self.boxes[self.source]:
        if box.x1 == top_left.x() and box.y1 == top_left.y():
            return box

def set_new_box_name(self, item: QGraphicsTextItem):
    """Переименовывание рамки"""
    name, ok = QInputDialog.getText(self, "Название области", "Введите новое название:")
    if ok:
        for box in self.boxes[self.source]:
            if box.name == item.toPlainText():
                item.setHtml(f'<div style="background:#008700;">{name}</p>')
                # изменение кнопок
                if self.isMetaButtons:
                    for button in self.metaButtons:
                        if self.metaButtons[button].text() == box.name:
                            removeMetaButtons(self, box.name)
                            addMetaButton(self, name)
                if self.isMetaComboBox:
                    removeMetaButtons(self, box.name)
                    addMetaComboBoxItems(self, name)
                box.name = name

def delete_box(self, item: QGraphicsRectItem):
    """Удаление рамки"""
    result = get_msg_result("Удаление","Удалить рамку?")
    if result:
        top_left = item.rect().topLeft()
        box = get_box_by_top_left(self, top_left)
        name_item = get_name_item_by_text(self, box.name)
        self.current_scene.removeItem(name_item)
        self.current_scene.removeItem(item)
        self.boxes[self.source].remove(box)
        # удаление соответствующей кнопки
        removeMetaButtons(self, box.name)

def load_boxes(self):
    """Загрузка сохраненных в файл данных о рамках"""
    if os.path.exists("./boxes.pickle"):
        with open("./boxes.pickle", "rb") as f:
            self.boxes = pickle.load(f)