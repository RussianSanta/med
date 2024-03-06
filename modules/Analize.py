from PyQt6.QtWidgets import (QWidget, QInputDialog, QMessageBox, QHBoxLayout, 
                             QComboBox, QCheckBox, QPushButton)
from PyQt6.QtCore import QSize
from PyQt6 import uic
import os
from modules.messages import get_msg_result
from modules.AnalizeWindow import AnalizeWindow

class Analize(QWidget):
    """ Класс отвечающий за инициализацию и работу окна выбора модулей """
    def __init__(self, parent):
        super().__init__() 
        uic.loadUi('ui/analize_modules.ui', self)
        self.parent = parent
        self.move(self.parent.x()+740, self.parent.y()+75)
        self.btnAddModule.clicked.connect(self.addModule)
        self.btnModuleSelection.clicked.connect(self.selectModule)
        self.modules = dict()
        self.unitsPath = "./units/"
        self.loadPrevModules()
        self.show()

    def loadPrevModules(self):
        if os.path.exists(self.unitsPath):
            for dir in os.listdir(self.unitsPath):
                self.addModuleLine(dir)
        else:
            os.mkdir("units")

    def addModule(self):
        """ Добавление модуля """
        dialog = QInputDialog(self)
        dialog.setWindowTitle("HELLO!")
        dialog.setStyleSheet("* { color: white }")
        name, ok = dialog.getText(self, "Добавление модуля", "Введите название прикладного модуля:")
        if ok:
            os.mkdir(self.unitsPath+"/"+name)
            self.addModuleLine(name)
            
    def addModuleLine(self, name):
        moduleName = f'module-{name}'
        self.modules[moduleName] = QHBoxLayout()
        self.modules[moduleName].setObjectName(moduleName)
        self.checkBox = QCheckBox(parent=self.verticalLayoutWidget)
        self.checkBox.setObjectName(f"checkBox-{name}")
        self.checkBox.setText(name)
        self.modules[moduleName].addWidget(self.checkBox)
        self.comboBoxModules = QComboBox(parent=self.verticalLayoutWidget)
        self.comboBoxModules.setMaximumSize(QSize(80, 16777215))
        self.comboBoxModules.setObjectName(f"comboBox-{name}")
        self.comboBoxModules.addItem("на форме")
        self.comboBoxModules.addItem("в окне")
        self.modules[moduleName].addWidget(self.comboBoxModules)
        self.deleteModuleButton = QPushButton(parent=self.verticalLayoutWidget)
        self.deleteModuleButton.setMinimumSize(QSize(20, 20))
        self.deleteModuleButton.setMaximumSize(QSize(20, 20))
        self.deleteModuleButton.setObjectName(f"deleteModuleButton-{name}")
        self.deleteModuleButton.setText("-")
        self.deleteModuleButton.clicked.connect(lambda: self.deleteModule(name))
        self.modules[moduleName].addWidget(self.deleteModuleButton)
        self.verticalModulesListLayout.insertLayout(len(self.modules)-1, self.modules[moduleName])
    


    def deleteModule(self, name):
        """ Удаление модуля """
        moduleName = f'module-{name}'
        result = get_msg_result("Удаление","Удалить модуль?")
        if result:
            module = self.modules.pop(moduleName)
            module.setParent(None)
            self.deleteItemsOfLayout(module)
            os.rmdir(self.unitsPath+"/"+name)

    def deleteItemsOfLayout(self, layout):
        """ Удаление содержимого и самого Layout'а"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteItemsOfLayout(item.layout())
    
    def selectModule(self):
        for m in self.modules.keys():
            name = m.split('module-')[1]
            checkBoxName = f'checkBox-{name}'
            comboBoxName = f'comboBox-{name}'
            checkBox = self.findChild(QCheckBox, checkBoxName)
            if checkBox.isChecked():
                comboBoxSelection = self.findChild(QComboBox, comboBoxName).currentIndex()
                # selection = self.comboBoxModules.currentIndex()
                if comboBoxSelection == 0:
                    self.openAnalizeFrame()
                if comboBoxSelection == 1:
                    AnalizeWindow.openAnalizeWindow(self)

    def openAnalizeFrame(self):
        self.parent.frameProcessing.hide()
        self.loadAnalizeUI()
        self.parent.verticalFrame.show()

    def loadAnalizeUI(self):
        self.parent.verticalFrame

    def openAnalize(self):
        self.analize_choosing_window = Analize(self)