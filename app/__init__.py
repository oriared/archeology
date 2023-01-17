from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import toml
import os


def config_path():
    if os.path.exists(os.path.abspath('config.toml')):
        return os.path.abspath('config.toml')
    else:
        return os.path.abspath('example_config.toml')


app = Flask(__name__)
app.config.from_file(config_path(), load=toml.load)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Авторизуйтесь, чтобы получить возможность добавлять \
    статьи'
bootstrap = Bootstrap(app)
moment = Moment(app)


from . import routes, models, errors
