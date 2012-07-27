# -*- coding: utf-8 -*-
# file: pdfrog/editarticletagsdialog.py
from PySide.QtCore import *
from PySide.QtGui import *
import pdfrog
from pdfrog.datamodel import Article, Tag
from pdfrog.customwidgets import QLineEdit_focus, QListWidget_focus

class EditArticleTagsDialog(QDialog):
    def __init__(self, parent, article):
        QDialog.__init__(self, parent)
        self.article = article
        self.setWindowTitle("Edit tag list")

        self.createWidgets()
        self._setButtonDirection(to=True)
        self.updateTagList()
        self.updateArticleTagList()
        self.tag_source = "nowhere"

    def createWidgets(self):
        self.article_tag_list = QListWidget_focus()
        self.tag_list = QListWidget_focus()
        self.tag_name = QLineEdit_focus()
        self.add_tag_to_article = QPushButton("←")
        self.remove_tag_from_article = QPushButton("→")
        self.dialog_buttons = QDialogButtonBox()
        self.dialog_buttons.addButton("Close", QDialogButtonBox.AcceptRole)

        # widget parameters
        self.article_tag_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tag_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # signals
        self.dialog_buttons.accepted.connect(self.accept)
        self.add_tag_to_article.clicked.connect(self.addTagToArticle)
        self.remove_tag_from_article.clicked.connect(self.removeTagFromArticle)
        self.tag_name.textChanged.connect(self._tagNameTextChanged)
        self.tag_name.returnPressed.connect(self._tagNameReturnPressed)
        self.tag_name.cursorPositionChanged.connect(self._tagNameCursorPositionChanged)
        self.tag_list.currentRowChanged.connect(self._tagListCurrentRowChanged)
        self.tag_list.itemActivated.connect(self._tagListItemActivated)
        self.article_tag_list.currentRowChanged.connect(self._articleTagListCurrentRowChanged)
        self.article_tag_list.itemActivated.connect(self._articleTagListItemActivated)

        # arrange widgets
        main_vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        main_vbox.addLayout(hbox1, stretch=1)
        main_vbox.addWidget(self.dialog_buttons)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(QLabel("Article tag list:"))
        vbox1.addWidget(self.article_tag_list, stretch=1)
        hbox1.addLayout(vbox1, stretch=1)

        vbox2 = QVBoxLayout()
        vbox2.addStretch(stretch=1)
        vbox2.addWidget(self.add_tag_to_article)
        vbox2.addWidget(self.remove_tag_from_article)
        vbox2.addStretch(stretch=1)
        hbox1.addLayout(vbox2)

        vbox3 = QVBoxLayout()
        vbox3.addWidget(QLabel("Tag:"))
        vbox3.addWidget(self.tag_name)
        vbox3.addWidget(QLabel("Tag list:"))
        vbox3.addWidget(self.tag_list, stretch=1)
        hbox1.addLayout(vbox3, stretch=1)

        self.setLayout(main_vbox)

    def _setButtonDirection(self, to=True):
        self.add_tag_to_article.setEnabled(to)
        self.remove_tag_from_article.setEnabled(not to)

    def updateTagList(self):
        self.tag_list.clear()
        like_string = '%' + self.tag_name.text() + '%'
        for tag in pdfrog.session.query(Tag).filter(Tag.name.like(like_string)).limit(300):
            self.tag_list.addItem(tag.name)

    def updateArticleTagList(self):
        self.article_tag_list.clear()
        for tag in self.article.tags:
            self.article_tag_list.addItem(tag.name)

    def addTagToArticle(self):
        if self.tag_source == "list":
            items = self.tag_list.selectedItems()
            for item in items:
                self.article.addTagByName(item.text())
        elif self.tag_source == "edit":
            self.article.addTagByName(self.tag_name.text())
        self.updateArticleTagList()

    def removeTagFromArticle(self):
        items = self.article_tag_list.selectedItems()
        if len(items) != 0:
            for item in items:
                self.article.removeTagByName(item.text())
        self.updateArticleTagList()

    def _tagNameTextChanged(self, text):
        self.tag_source = "edit"
        self.updateTagList()

    def _tagNameCursorPositionChanged(self, old, new):
        self.tag_source = "edit"
        self._setButtonDirection(to=True)

    def _tagNameReturnPressed(self):
        self.tag_source = "edit"
        self.article.addTagByName(self.tag_name.text())
        self.updateArticleTagList()

    def _tagListCurrentRowChanged(self, row):
        self.tag_source = "list"
        self._setButtonDirection(to=True)

    def _tagListItemActivated(self, item):
        self.tag_source = "list"
        self.article.addTagByName(item.text())
        self.updateArticleTagList()

    def _articleTagListCurrentRowChanged(self, row):
        self._setButtonDirection(to=False)

    def _articleTagListItemActivated(self, item):
        self.article.removeTagByName(item.text())
        self.updateArticleTagList()
