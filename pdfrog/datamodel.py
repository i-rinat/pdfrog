# -*- coding: utf-8 -*-
# file: pdfrog/datamodel.py
import sqlalchemy as sa
import sqlalchemy.ext.declarative
from sqlalchemy import func
import pdfrog

Base = sa.ext.declarative.declarative_base()

author_article_pairs = sa.Table ('author_article_pairs', Base.metadata,
    sa.Column ('author_id', sa.Integer, sa.ForeignKey('authors.id')),
    sa.Column ('article_id', sa.Integer, sa.ForeignKey('articles.id'))
)

article_tag_pairs = sa.Table('article_tag_pairs', Base.metadata,
    sa.Column('article_id', sa.Integer, sa.ForeignKey('articles.id')),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('article_tags.id'))
)

author_tag_pairs = sa.Table('author_tag_pairs', Base.metadata,
    sa.Column('author_id', sa.Integer, sa.ForeignKey('authors.id')),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('author_tags.id'))
)

class Author(Base):
    __tablename__ = 'authors'
    id =            sa.Column(sa.Integer, primary_key=True)
    name =          sa.Column(sa.String, unique=True)
    organization =  sa.Column(sa.String)
    birthday =      sa.Column(sa.Date)
    info =          sa.Column(sa.String)
    notes =         sa.Column(sa.String)
    tags =          sa.orm.relationship('AuthorTag', secondary=author_tag_pairs, backref='authors')

    def getArticleCount(self):
        """counts article count this author have"""
        cnt = pdfrog.session.query(author_article_pairs).\
            filter(author_article_pairs.c.author_id == self.id).count()
        return cnt

    def getArticleTags(self):
        tags = set()
        article_list = pdfrog.session.query(Article).join(Article.authors).filter(Author.id==self.id)
        for article in article_list:
            for tag in article.tags:  tags.add(tag)
        return sorted(tags, key=lambda tag: tag.name)

    def removeFromDatabase(self):
        pdfrog.session.delete(self)

class Article(Base):
    __tablename__ = 'articles'
    id =          sa.Column(sa.Integer, primary_key = True)
    title =       sa.Column(sa.String)
    authors =     sa.orm.relationship('Author', secondary=author_article_pairs, backref='articles')
    tags =        sa.orm.relationship('Tag', secondary=article_tag_pairs, backref='articles')
    keywords =    sa.Column(sa.String)
    abstract =    sa.Column(sa.String)
    plaintext =   sa.Column(sa.String)
    fileblob =    sa.Column(sa.Binary)
    filemime =    sa.Column(sa.String)   # mime
    filecompr =   sa.Column(sa.String)   # compression
    filesize =    sa.Column(sa.Integer)
    md5 =         sa.Column(sa.String)
    j_issue_id =  sa.Column(sa.Integer, sa.ForeignKey('journalissues.id'))
    journal_issue = sa.orm.relationship('JournalIssue', backref=sa.orm.backref('articles', order_by=id))
    recieved =    sa.Column(sa.Date)
    revised =     sa.Column(sa.Date)
    published =   sa.Column(sa.Date)
    pages_from =  sa.Column(sa.Integer)
    pages_to =    sa.Column(sa.Integer)
    pages_total = sa.Column(sa.Integer)

    def addTagByName(self, tagname):
        if tagname == "": return
        tags = pdfrog.session.query(Tag).filter(Tag.name == tagname).limit(1)
        if tags.count() == 0:
            tag = Tag()
            tag.name = tagname
        else:
            tag = tags[0]
        if self.tags.count(tag) == 0:
            self.tags.append(tag)

    def removeTagByName(self, tagname):
        tags = pdfrog.session.query(Tag).filter(Tag.name == tagname).limit(1)
        if tags.count() != 0:
            tag = tags[0]
            if self.tags.count(tag) != 0: self.tags.remove(tag)

    def addAuthorByName(self, authorname):
        if authorname == "": return None
        authors = pdfrog.session.query(Author).filter(Author.name == authorname).limit(1)
        if authors.count() > 0:
            author = authors[0]
        else:
            author = Author()
            author.name = authorname
        if self.authors.count(author) == 0: self.authors.append(author)
        return author

    def removeAuthorByName(self, authorname):
        authors = pdfrog.session.query(Author).filter(Author.name == authorname).limit(1)
        if authors.count() > 0:
            author = authors[0]
            if self.authors.count(author) > 0: self.authors.remove(author)


class Tag(Base):
    __tablename__ = 'article_tags'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True)

    def getUsageCount(self):
        """count how many times this tag used"""
        cnt = pdfrog.session.query(article_tag_pairs).filter(article_tag_pairs.c.tag_id == self.id).count()
        return cnt

    def discharge(self):
        """remove this tag from all articles (results in no its usage at all)"""
        query = pdfrog.session.query(Article).join(article_tag_pairs).\
                    filter(article_tag_pairs.c.tag_id == self.id)
        for article in query:
            article.tags.remove(self)

class AuthorTag(Base):
    __tablename__ = 'author_tags'
    id =   sa.Column(sa.Integer, primary_key=True)
    name =  sa.Column(sa.String)

class Journal(Base):
    __tablename__ = 'journals'
    id =      sa.Column(sa.Integer, primary_key=True)
    title =   sa.Column(sa.String)

class JournalIssue(Base):
    __tablename__ = 'journalissues'
    id =         sa.Column(sa.Integer, primary_key=True)
    year =       sa.Column(sa.Integer)
    journal_id = sa.Column(sa.Integer, sa.ForeignKey('journals.id'))
    journal =    sa.orm.relationship('Journal', backref=sa.orm.backref('journalissues', order_by=id))
