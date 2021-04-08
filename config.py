import json
import datetime
import os
import vimeo
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    # To access secrets stored in secrets.ejson, you must first decrypt them.
    # Decrypt the secrets.ejson by following the steps below:
    #   1. Paste your private key in the file: `/opt/ejson/keys/<public key>`
    #   2. Run the command: `ejson decrypt secrets.ejson` which outputs secrets.ejson in plaintext to stdout
    #   3. Copy the plaintext from stdout and paste it in secrets.ejson, overwriting the ciphertext

    # IMPORTANT: To prevent secrets leaking, re-encrypt secrets.ejson before committing to version control.
    # Run `ejson encrypt secrets.ejson` to encrypt secrets.ejson
    # (secrets.ejson is included in .gitignore as an extra precaution)
    # See https://github.com/Shopify/ejson for detailed instructions.

    with open('secrets.ejson') as ejson_file:
        secretsData = json.load(ejson_file)

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 1024 * 1024 * 50
    UPLOAD_EXTENSIONS = ['.mp4', '.mov', '.wmv', '.avi']
    UPLOAD_PATH = 'uploads'

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(weeks=52)

    SECRET_KEY = secretsData["SECRET_KEY"]
    JWT_SECRET_KEY = SECRET_KEY

    VIMEO_CLIENT = secretsData["VIMEO_CLIENT"]
    VIMEO_CLIENT = vimeo.VimeoClient(
        token=VIMEO_CLIENT.token,
        key=VIMEO_CLIENT.key,
        secret=VIMEO_CLIENT.secret
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
