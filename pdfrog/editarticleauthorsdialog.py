# -*- coding: utf-8 -*-
# file: pdfrog/editarticleauthorsdialog.py
from PySide.QtCore import *
from PySide.QtGui import *
import pdfrog
from pdfrog.datamodel import Article, Author
from pdfrog.customwidgets import QLineEdit_focus, QListWidget_focus

class EditArticleAuthorsDialog(QDialog):
    def __init__(self, parent, article):
        QDialog.__init__(self, parent)
        self.parent = parent
        self.article = article

        self.setWindowTitle('Edit author list')
        self.createWidgets()
        self.updateAuthorList()
        self.updateArticleAuthorList()
        self.author_name.setFocus()
        self.author_source = "nowhere"

    def createWidgets(self):
        self.author_name = QLineEdit_focus()
        self.author_list = QListWidget_focus()
        self.article_author_list = QListWidget_focus()
        self.author_info = QTextEdit()
        self.add_to_article_button = QPushButton("↑")
        self.remove_from_article_button = QPushButton("↓")
        dialog_buttons = QDialogButtonBox()
        dialog_buttons.addButton("Close", QDialogButtonBox.AcceptRole)

        # parameters
        self.author_list.setSortingEnabled(True)
        self.author_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.article_author_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._setButtonDirection(to=True)

        # signals
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)
        self.author_name.textChanged.connect(self.authorNameTextChanged)
        self.author_name.cursorPositionChanged.connect(self.authorNameCursorPositionChanged)
        self.author_name.returnPressed.connect(self.authorNameReturnPressed)
        self.author_list.currentRowChanged.connect(self.authorListCurrentRowChanged)
        self.author_list.itemActivated.connect(self.authorListItemActivated)
        self.add_to_article_button.clicked.connect(self.addToArticleButtonClicked)
        self.remove_from_article_button.clicked.connect(self.removeFromArticleButtonClicked)
        self.article_author_list.currentRowChanged.connect(self.articleAuthorListCurrentRowChanged)
        self.article_author_list.itemActivated.connect(self.articleAuthorListItemActivated)

        # widget packing
        hbox1 = QHBoxLayout()

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.add_to_article_button, stretch=1)
        hbox2.addWidget(self.remove_from_article_button, stretch=1)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(QLabel("Article's authors:"))
        vbox1.addWidget(self.article_author_list, stretch=1)
        vbox1.addLayout(hbox2)
        vbox1.addWidget(self.author_name)
        vbox1.addWidget(QLabel("All authors:"))
        vbox1.addWidget(self.author_list, stretch=2)
        hbox1.addLayout(vbox1, stretch=1)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.author_info, stretch=1)
        vbox2.addWidget(dialog_buttons)
        hbox1.addLayout(vbox2, stretch=3)

        self.setLayout(hbox1)

    def _setButtonDirection(self, to):
        self.add_to_article_button.setEnabled(to)
        self.remove_from_article_button.setEnabled(not to)

    def updateAuthorList(self):
        self.author_list.clear()
        like_expr = '%' + self.author_name.text() + '%'
        for author in pdfrog.session.query(Author).filter(Author.name.like(like_expr)).limit(300):
            self.author_list.addItem(author.name)

    def updateArticleAuthorList(self):
        self.article_author_list.clear()
        for author in self.article.authors:
            self.article_author_list.addItem(author.name)

    def authorNameTextChanged(self):
        self._setButtonDirection(to=True)
        self.updateAuthorList()

    def updateAuthorInfo(self, author_name):
        author = pdfrog.session.query(Author).filter(Author.name == author_name)[0]
        self.author_info.setText(author.notes)

    def authorListCurrentRowChanged(self, row):
        if row == -1: return
        self.author_source = "list"
        self._setButtonDirection(to=True)
        author_name = self.author_list.item(row).text()
        self.updateAuthorInfo(author_name)

    def authorListItemActivated(self, item):
        self._setButtonDirection(to=True)
        self.article.addAuthorByName(item.text())
        self.updateArticleAuthorList()

    def addToArticleButtonClicked(self):
        if self.author_source == "edit":
            self.article.addAuthorByName(self.author_name.text())
        elif self.author_source == "list":
            for item in self.author_list.selectedItems():
                self.article.addAuthorByName(item.text())
        self.updateArticleAuthorList()

    def removeFromArticleButtonClicked(self):
        for item in self.article_author_list.selectedItems():
            self.article.removeAuthorByName(item.text())
        self.updateArticleAuthorList()

    def articleAuthorListCurrentRowChanged(self, row):
        if row == -1: return
        self._setButtonDirection(to=False)
        self.author_source = "list"
        author_name = self.article_author_list.item(row).text()
        self.updateAuthorInfo(author_name)

    def articleAuthorListItemActivated(self, item):
        self.article.removeAuthorByName(item.text())
        self.updateArticleAuthorList()

    def authorNameCursorPositionChanged(self, arg1, arg2):
        self._setButtonDirection(to=True)
        self.author_source = "edit"

    def authorNameReturnPressed(self):
        self.article.addAuthorByName(self.author_name.text())
        self.updateArticleAuthorList()
