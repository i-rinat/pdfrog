# -*- coding: utf-8 -*-
# file: pdfrog/authoreditdialog.py

from PySide.QtCore import *
from PySide.QtGui import *

class AuthorEditDialog(QDialog):
    def __init__(self, parent=None, author=None):
        self.parent = parent
        self.author = author
        QDialog.__init__(self, parent)
        if author is None:
            raise Exception("AuthorEditDialog must be supplied with author")

        self.setWindowTitle("Edit author")
        self.resize(500, 300)
        self.createWidgets()
        self.fillFields()

    def createWidgets(self):
        # widgets
        self.author_name = QLineEdit()
        self.author_organization = QLineEdit()
        self.author_info = QTextEdit()
        self.author_notes = QTextEdit()
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Name:"))
        vbox.addWidget(self.author_name)
        vbox.addWidget(QLabel("Organization:"))
        vbox.addWidget(self.author_organization)
        vbox.addWidget(QLabel("Info:"))
        vbox.addWidget(self.author_info, stretch=1)
        vbox.addWidget(QLabel("Notes:"))
        vbox.addWidget(self.author_notes, stretch=1)
        vbox.addWidget(button_box)

        self.setLayout(vbox)

    def collectFields(self):
        self.author.name = self.author_name.text()
        self.author.organization = self.author_organization.text()
        self.author.info = self.author_info.toHtml()
        self.author.notes = self.author_notes.toHtml()

    def fillFields(self):
        self.author_name.setText(self.author.name)
        self.author_organization.setText(self.author.organization)
        self.author_info.setHtml(self.author.info)
        self.author_notes.setHtml(self.author.notes)

    def accept(self):
        # fill author fields before leaving
        self.collectFields()
        return QDialog.accept(self)
