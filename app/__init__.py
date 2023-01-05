from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import config


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Авторизуйтесь, чтобы получить возможность добавлять \
    статьи'


from . import routes, models, errors
