from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import config


app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or config.DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from . import routes, models, errors
