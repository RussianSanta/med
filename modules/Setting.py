from PyQt6.QtWidgets import QWidget, QFileDialog

from PyQt6 import uic
from modules.meta import (addMeta)

class Setting(QWidget):
    """Класс отвечающий за инициализацию и работу окна настроек"""

    def __init__(self, parent):
        super().__init__() 
        uic.loadUi('ui/setting.ui', self)
        self.parent = parent
        self.move(self.parent.x()+740, self.parent.y()+75)
        self.btnSavePath.clicked.connect(self.getSavePath)
        self.editSavePath.setText(self.parent.cameraRecordsSavePath)
        self.editRecordTime.setText(str(self.parent.recordTime))
        self.btnSaveSetting.clicked.connect(self.saveSetting)
        # self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        if self.parent.isMetaButtons:
            self.radioLenta.setChecked(self.parent.isMetaButtons)
        if self.parent.isMetaComboBox:
            self.radioList.setChecked(self.parent.isMetaComboBox)
        self.show()
    
    def getSavePath(self):
        self.savePath = QFileDialog.getExistingDirectory(self)
        self.editSavePath.setText(self.savePath)
    
    def saveSetting(self):
        self.parent.recordTime = float(self.editRecordTime.text().replace(',', '.'))
        self.parent.cameraRecordsSavePath = self.editSavePath.text()
        print('Установленное время для записи: ' + str(self.parent.recordTime))
        print('Директория для сохранения записи: ' + self.parent.cameraRecordsSavePath)
        self.parent.isMetaButtons = self.radioLenta.isChecked()
        self.parent.isMetaComboBox = self.radioList.isChecked()
        if self.parent.source is not None:
            addMeta(self.parent)
        self.close()

    def openSetting(self):
        self.setting_window = Setting(self)
