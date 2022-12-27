from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login 


@login.user_loader
def load_user(user_id):
    return Author.query.get(int(user_id))


class Author(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_author = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))
    password_hash = db.Column(db.String(128))

    articles = db.relationship('Article', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_section = db.Column(db.String(50), nullable=False)

    articles = db.relationship('Article', secondary='asera')


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_region = db.Column(db.String(50), nullable=False)


class Ethnos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_ethnos = db.Column(db.String(50), nullable=False)


class Age(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_age = db.Column(db.String(50), nullable=False)
    period = db.Column(db.String(50))


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_tag = db.Column(db.String(50), nullable=False)

    #articles =...


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_subscriber = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100))

    tags = db.relationship('Tag', secondary='subscriber_tag')
    authors = db.relationship('Author', secondary='subscriber_author')


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    text = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    created_on = db.Column(db.Date, default=datetime.utcnow)
    updated_on = db.Column(db.Date)

    #tags =...


class Asera(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('article_id', 'section_id', 'region_id', 'age_id', 'ethnos_id'),)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    age_id = db.Column(db.Integer, db.ForeignKey('age.id'))
    ethnos_id = db.Column(db.Integer, db.ForeignKey('ethnos.id'))


class TagArticle(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('tag_id', 'article_id'),)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


class SubscriberTag(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('subscriber_id', 'tag_id'),)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))


class SubscriberAuthor(db.Model):
    __table_args__ = (db.PrimaryKeyConstraint('subscriber_id', 'author_id'),)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('subscriber.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
