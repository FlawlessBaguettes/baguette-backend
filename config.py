import json
import datetime
import os
import vimeo
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):

    # Secrets are stored in secrets.ejson, an encrypted JSON file.
    # Before running the server, you need to locally decrypt secrets.ejson so they can be accessed at runtime.
    # Decrypt secrets.ejson by following the steps below:
    #
    #   1. Copy the public key from the top of secrets.ejson (this value is always in plaintext)
    #   2. Create a file named after your public key in `/opt/ejson/keys` by running:
    #      `touch /opt/ejson/keys/<PUBLIC_KEY_HERE>`
    #   3. Copy and paste the associated private key into the file created in step 2.
    #   4. Decrypt secrets.ejson by running: `ejson decrypt secrets.ejson`.
    #      This will output secrets.ejson in plaintext to stdout.
    #   5. Overwrite secrets.ejson with the plaintext outputted in step 4.
    #
    # IMPORTANT: To prevent secrets leaking, ensure secrets.ejson is encrypted before committing any changes
    # to the file into version control. Run `ejson encrypt secrets.ejson`.
    #
    # For more info on ejson, see https://github.com/Shopify/ejson

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
        token=VIMEO_CLIENT["token"],
        key=VIMEO_CLIENT["key"],
        secret=VIMEO_CLIENT["secret"]
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
