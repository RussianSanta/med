import numpy as np
from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot, QSize
from PyQt6.QtGui import QImage, QPixmap, QColor, QIcon
from PyQt6.QtWidgets import (QStyle, QMainWindow, QGraphicsTextItem, QFrame,
                             QInputDialog, QGraphicsRectItem, QGraphicsEllipseItem, 
                              QApplication, QGraphicsScene, QGraphicsPixmapItem)

from typing import List, Dict
from collections import defaultdict
import pickle

# classes and funsctions
from modules.openImage import openImage
from modules.openVideo import openVideo
from modules.openCamera import openCamera
from modules.processing import (openProcessingFrame, processingOn, 
                        toggleProcessing, processFrame, scalingFrame)
from modules.meta import (addMetaButton, addMetaComboBoxItems, metaClickAction)

from modules.VideoThread import VideoThread
from modules.models import Box, CropPoint
from modules.Setting import Setting
from modules.Analize import Analize
from modules.messages import get_msg_result
from modules.boundingBoxes import (get_rectangle, get_rectangle_name, load_boxes, 
                                    set_new_box_name, delete_box)

# UI
# from ui.app_ui import Ui_MainWindow
# from ui.analize import Ui_AnalizeForm

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setupUi(self) # из файла .py с помощью pyuic6 ui\app.ui -o ui\app_ui.py
        uic.loadUi('ui/app.ui', self) # напрямую из ui-файла
        self.centralwidget.setContentsMargins(5, 5, 5, 5)

        self.thread = None # существует ли поток
        self.video_thread = None # экземпляр класса Fullscreen
        self.cut_video_thread = None  # обрезанный видеотред
        self.scale = 0.0
        self.threadOn = False # поток активирован
        self.current_scene = None # текущее заполнение области GraphicsView
        self.source = None # источник изображения/видеопотока
        self.recordTime = 0 # значение для сохранения времени записи в минутах
        self.metaButtons = dict() 
        self.cameraRecordsSavePath = "./example_media/CameraRecords"
        self.isChanged = False # флаг для проверки изменений
        self.originalImage = None # текущее оригинальное изображение
        self.transformedImage = None
        self.isOriginal = False # флаг оригинального изображения
        self.isMetaButtons = True # флаги выбора вида meta
        self.isMetaComboBox = False
        self.scaleFactor = self.scaleSlider.value()/100
        # self.isAnalizeInMainWindow = True

        # поведение и внешний вид кнопок
        self.actionOpenImage.triggered.connect(lambda: openImage(self))
        self.actionOpenImage.setShortcut("Ctrl+O")
        self.actionOpenVideo.triggered.connect(lambda: openVideo(self))
        self.actionOpenCamera.triggered.connect(lambda: openCamera(self))

        self.menuSetting.aboutToShow.connect(lambda: Setting.openSetting(self)) # открытие окна настройки

        self.graphicsView.mousePressEvent = self.onMouseClick
        self.fullscreenToggle.clicked.connect(self.openFullscreenWindow)
        self.playButton.clicked.connect(lambda: VideoThread.toggle_video(self))
        self.playButton.setDisabled(True)
        # сигналы к обработке изображения
        self.menuProcessing.aboutToShow.connect(lambda: openProcessingFrame(self)) # открытие формы для обработки изображения
        self.frameProcessing.hide()
        self.toggleProcessingButton.clicked.connect(lambda: toggleProcessing(self))
        self.convertToGrayCheckBox.clicked.connect(lambda: processingOn(self))
        self.binarizationCheckBox.clicked.connect(lambda: processingOn(self))
        self.binarizationSlider.valueChanged[int].connect(lambda: processingOn(self))
        self.binarizationValue.setText(str(self.binarizationSlider.value()))
        self.scaleSlider.valueChanged[int].connect(lambda: processingOn(self))
        self.scaleValue.setText(str(self.scaleSlider.value()))
        # анализ
        self.menuAnalize.aboutToShow.connect(lambda: Analize.openAnalize(self)) # открытие формы для анализа
        self.verticalFrame.hide()
        # self.verticalFrame.

        self.playIcon = self.style().standardIcon(getattr(QStyle.StandardPixmap, "SP_MediaPlay"))
        self.pauseIcon = self.style().standardIcon(getattr(QStyle.StandardPixmap, "SP_MediaPause"))
        self.playButton.setIcon(self.playIcon)

        self.box: List[CropPoint] = list()
        self.boxes: Dict[int, List[Box]] = defaultdict(list)
        load_boxes(self)

    def openFullscreenWindow(self):
        """ Открытие полноэкранного режима """
        self.rightGridFrame.hide()
        self.processingLabel.hide()
        self.menubar.hide()
        self.metaFrame.hide()
        self.gridLayout_4.setColumnStretch(1, 0)  
        self.showFullScreen()
        icon = QIcon()
        icon.addPixmap(QPixmap("ui\\icons/exit-fullscreen.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.fullscreenToggle.setIcon(icon)
        self.fullscreenToggle.setIconSize(QSize(24, 24))
        self.fullscreenToggle.clicked.disconnect(self.openFullscreenWindow)
        self.fullscreenToggle.clicked.connect(self.closeFullscreenWindow)

    def closeFullscreenWindow(self):
        """ Закрытие полноэкранного режима """
        self.rightGridFrame.show()
        self.processingLabel.show()
        self.menubar.show()
        self.metaFrame.show()
        self.gridLayout_4.setColumnStretch(1, 2)  
        self.showNormal()
        icon = QIcon()
        icon.addPixmap(QPixmap("ui\\icons/fullscreen-12-48.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.fullscreenToggle.setIcon(icon)
        self.fullscreenToggle.setIconSize(QSize(16, 16))
        self.fullscreenToggle.clicked.disconnect(self.closeFullscreenWindow)
        self.fullscreenToggle.clicked.connect(self.openFullscreenWindow)
    
    def closePreviousThread(self):
        """ Закрытие предыдущих потоков, если они есть """
        if self.video_thread is not None:
            self.video_thread.resume()
            self.threadOn = False 
            self.video_thread.close()

    @pyqtSlot(np.ndarray)
    def update_frame(self, image):
        """Установка изображения в окно"""
        # обработка изображения
        if self.toggleProcessingButton.isChecked():
            image = processFrame(self, image)
            image = scalingFrame(self, image)
        else:
            self.scaleFactor = 1.0
            
        # перевод изображения из CV2 в формат QImage в зависимости от проделанной обработки
        if self.convertToGrayCheckBox.isChecked() or self.binarizationCheckBox.isChecked():
            height, width = image.shape
            image = QImage(image.data, width, height, width, QImage.Format.Format_Grayscale8)
        else:
            height, width, channel = image.shape
            bytesPerLine = 3 * width
            image = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        scene = QGraphicsScene(self)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.current_scene = scene
        self.graphicsView.setScene(scene)

        # обновление актуальных рамок
        if self.isOriginal and self.source in self.boxes:
            for box in self.boxes[self.source]:
                self.current_scene.addItem(get_rectangle_name(box.name, box.x1*self.scaleFactor, box.y1*self.scaleFactor))
                self.current_scene.addItem(get_rectangle(box.x1*self.scaleFactor, box.y1*self.scaleFactor, box.x2*self.scaleFactor, box.y2*self.scaleFactor))
    
    def pauseThread(self, name):
        """ Приостановка видеопотока при переключения между метакнопками """
        if self.video_thread is not None: #  and self.threadOn
            self.originalImage = self.video_thread.pause()
            self.transformedImage = self.originalImage
            # time.sleep(1)
            self.threadOn = False
            metaClickAction(self, name)
            self.playButton.setIcon(self.playIcon)

    def onMouseClick(self, event):
        """ Обработчик нажатия ЛКМ на объект graphicsView"""
        if self.isOriginal:
            pos = event.pos()
            pos_scene = self.graphicsView.mapToScene(pos)

            item = self.current_scene.itemAt(pos_scene, self.graphicsView.transform())
            if isinstance(item, QGraphicsTextItem):
                set_new_box_name(self, item)
                return
            elif isinstance(item, QGraphicsRectItem):
                delete_box(self, item)
                return

            x, y = pos_scene.x() - 4, pos_scene.y() - 6
            point = QGraphicsEllipseItem(x, y, 4, 4)
            point.setBrush(QColor(0, 255, 0))
            self.current_scene.addItem(point)
            self.box.append(CropPoint(x, y, point))

            if len(self.box) == 2:
                name, ok = QInputDialog.getText(self, "Название области", "Введите название:")
                if ok:
                    text = get_rectangle_name(name, self.box[0].x, self.box[0].y)
                    rect = get_rectangle(self.box[0].x, self.box[0].y, self.box[1].x, self.box[1].y)
                    self.current_scene.addItem(text)
                    self.current_scene.addItem(rect)
                    box = Box(name, self.box[0].x, self.box[0].y, self.box[1].x, self.box[1].y)
                    self.boxes[self.source].append(box)
                    if self.isMetaButtons:
                        addMetaButton(self, box.name)
                    if self.isMetaComboBox:
                        addMetaComboBoxItems(self, box.name)

                # Удаляем выбранные точки
                for point in self.box:
                    self.current_scene.removeItem(point.point)
                self.box.clear()

    def closeEvent(self, event):
        """ Обработчик закрытия окна """
        self.closePreviousThread()
        if self.isChanged and get_msg_result("Завершение работы", "Сохранить изменения перед выходом?"):
            with open("./boxes.pickle", "wb") as f:
                pickle.dump(self.boxes, f)





if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MyWindow = MainWindow()
    MyWindow.show()
    sys.exit(app.exec())
