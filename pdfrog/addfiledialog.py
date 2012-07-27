# -*- coding: utf-8 -*-
# file: pdfrog/addfiledialog.py
from PySide.QtGui import *
from PySide.QtCore import *
from pdfrog.datamodel import Article
import pdfrog
import hashlib
import mimetypes

class AddFileDialog(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self.resize(600, 300)

        self.total_count = 1
        self.current_idx = 1
        self.__updateTitle()

        layout = QGridLayout()

        self.file_name = QLineEdit()
        self.file_name.setReadOnly(True)
        self.article_title = QLineEdit()
        self.article_title.setPlaceholderText("Change ...")

        self.file_size = QLabel()

        layout.addWidget(QLabel("File path:"), 0, 0)
        layout.addWidget(self.file_name, 0, 1)

        layout.addWidget(QLabel("Size:"), 1, 0)
        layout.addWidget(self.file_size, 1, 1)

        layout.addWidget(QLabel("Title:"), 2, 0)
        layout.addWidget(self.article_title, 2, 1)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(3, 1)

        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonbox.rejected.connect(self.reject)
        buttonbox.accepted.connect(self.doAddFile)

        vbox = QVBoxLayout()
        vbox.addItem(layout)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def setFileName(self, name):
        self.file_name.setText(name)
        self.article_title.setText(QFileInfo(name).fileName())
        self.article_title.setFocus()
        self.article_title.selectAll()

    def doAddFile(self):
        article = Article()
        mime = mimetypes.guess_type(self.file_name.text())
        with open(self.file_name.text(), 'rb') as f:
            article.fileblob = f.read()
        article.md5 = hashlib.md5(article.fileblob).hexdigest()
        article.title = self.article_title.text()
        article.filemime = mime[0]
        article.filecompr = mime[1]
        article.addTagByName("new")
        pdfrog.session.add(article)
        pdfrog.session.flush()
        self.accept()

    def setTotalCount(self, cnt):
        self.total_count = cnt
        self.__updateTitle()

    def setCurrent(self, idx):
        self.current_idx = idx
        self.__updateTitle()

    def __updateTitle(self):
        self.setWindowTitle("add article ({0} of {1})".format(self.current_idx, self.total_count))
