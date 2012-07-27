# -*- coding: utf-8 -*-
# file: pdfrog/taglistwidget.py
from PySide.QtGui import *
from PySide.QtCore import *
import pdfrog
from .datamodel import Tag
import sqlalchemy as sa

class TagList(QTableView):
    def __init__(self, *args):
        QTableView.__init__(self, *args)
        mdl = TagListModel()
        self.setModel(mdl)
        self.horizontalHeader().setMovable(True)
        self.horizontalHeader().setHighlightSections(False)
        self.installEventFilter(self)
        self.verticalHeader().setVisible(False)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.refreshData()

    def refreshData(self):
        self.model().clearData()
        for tag in pdfrog.session.query(Tag):
            self.model().appendTag(tag)

    def removeSelectedTags(self):
        idxs = self.selectionModel().selectedRows()
        if all([self.item(idx.row()).getUsageCount()==0 for idx in idxs]):
            # all selected tags have zero usage count
            tag_names_list = [self.item(idx.row()).name for idx in idxs]

            res = QMessageBox.question(self, "Remove tags", \
                "Do you want to remove tags: \n{} ?".format(", ".join(tag_names_list)), \
                buttons = QMessageBox.Ok | QMessageBox.Cancel)

            for idx in idxs:
                tag = self.item(idx.row())
                pdfrog.session.delete(tag)

            self.refreshData()
        else:
            QMessageBox.warning(self, "Remove tags",
                "Can't remove tags with non-zero usage. " + \
                "You must manually discharge them first. Sorry.")

    def renameSelectedTag(self):
        """renames first selected tag. Asks user for new name"""
        idxs = self.selectionModel().selectedRows()
        if len(idxs) > 0:
            tag = self.item(idxs[0].row())
            (new_tag_name, ok_pressed) = QInputDialog.getText(self, "Rename tag", "New name:", text=tag.name)
            if ok_pressed and new_tag_name != "":
                tag.name = new_tag_name
                self.refreshData()

    def dischargeSelectedTags(self):
        """removes any use of the selected tags"""
        idxs = self.selectionModel().selectedRows()
        if len(idxs) == 0: return

        tag_names_list = [self.item(idx.row()).name for idx in idxs]

        res = QMessageBox.question(self, "Discharge tags",
            "Do you want to discharge tags:\n" + \
            ", ".join(tag_names_list), \
            buttons = QMessageBox.Ok | QMessageBox.Cancel)

        if res == QMessageBox.Ok:
            for idx in self.selectionModel().selectedRows():
                tag = self.item(idx.row())
                tag.discharge()

            self.refreshData()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.ContextMenu:
            self.context_menu.exec_(QCursor.pos())
            return True
        else:
            return QTableView.eventFilter(self, obj, event)

    def item(self, row):
        return self.model().item(row)


class TagListModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.view = parent
        self.datastore = []

    COLUMN_TAG = 0
    COLUMN_TIMES_USED = 1

    def rowCount(self, parent=None):
        return len(self.datastore)

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None
        elif role == Qt.DisplayRole:
            if index.column() == self.COLUMN_TAG:
                return self.datastore[index.row()].name
            if index.column() == self.COLUMN_TIMES_USED:
                return self.datastore[index.row()].getUsageCount()
            else:
                return "Unknown"
        else:
            return None

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if column == self.COLUMN_TAG:
                return "Tag"
            elif column == self.COLUMN_TIMES_USED:
                return "Times used"
            else:
                return "Unknown"
        else:
            return None

    def clearData(self):
        self.modelReset.emit()
        self.datastore = []

    def appendTag(self, tag, update=True):
        if type(tag) != Tag:
            raise Exception("tag is not Tag")
        if update: self.beginInsertRows(QModelIndex(), len(self.datastore), len(self.datastore))
        self.datastore.append(tag)
        if update: self.endInsertRows()

    def sort(self, column, order):
        reverse = (order == Qt.DescendingOrder)
        self.layoutAboutToBeChanged.emit()

        if column == self.COLUMN_TAG:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.name, reverse=reverse)
        elif column == self.COLUMN_TIMES_USED:
            self.datastore = sorted(self.datastore, key=lambda obj: obj.getUsageCount(), reverse=reverse)

        self.layoutChanged.emit()

    def item(self, row):
        return self.datastore[row]
