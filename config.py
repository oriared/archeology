import os


basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-shall-not-pass'
    

class DevelopmentConfig(BaseConfig):
    FLASK_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:100@127.0.0.1:5432/bezvody-dev'
    CSRF_ENABLED = True


class TestingConfig(BaseConfig):
    FLASK_DEBUG = True    


class ProductionConfig(BaseConfig):
    FLASK_DEBUG = False    
