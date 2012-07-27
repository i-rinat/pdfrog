# -*- coding: utf-8 -*-
# file: pdfrog/customwidgets.py

from PySide.QtCore import *
from PySide.QtGui import *

class QLineEdit_focus(QLineEdit):
    """emits cursorPositionChanged when gets focus"""
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.returnPressed.emit()
            return True
        if event.type() == QEvent.FocusIn:
            self.cursorPositionChanged.emit(0, 1)
        return QLineEdit.eventFilter(self, obj, event)


class QListWidget_focus(QListWidget):
    """emits currentRowChanged signal when gets focus"""
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.currentRowChanged.emit(self.currentRow())
        return QListWidget.eventFilter(self, obj, event)
