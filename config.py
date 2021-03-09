import datetime
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 1024 * 1024 * 50
    UPLOAD_EXTENSIONS = ['.mp4', '.mov', '.wmv', '.avi']
    UPLOAD_PATH = 'uploads'

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(weeks=52)
    JWT_SECRET_KEY = SECRET_KEY


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
