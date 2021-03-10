import datetime
import os
import vimeo
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

    VIMEO_CLIENT = vimeo.VimeoClient(
        token='29b2d3f5fcbbf63d8f966f7c85973fe5',
        key='cd8615a35359c7d8bd60bb9766a9e9a80aa1ef01',
        secret='Xy1iTA658MNPtM8AjOezNafd33kaQx7s/Lw3rO5u8Swh6+xH1nsqCnO5eTt093n0y20kJc0mo/jEgWM/MxKjWH1wNc4zu/7VSyfbR55C4mWaEQvqvDvGm7Ay4EuVK/A4'
    )


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
