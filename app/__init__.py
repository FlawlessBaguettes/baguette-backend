from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import settings

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 10
app.config['UPLOAD_EXTENSIONS'] = ['.mp4', '.mov', '.wmv', '.avi']
app.config['UPLOAD_PATH'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_PATH']):
   os.makedirs(app.config['UPLOAD_PATH'])

db = SQLAlchemy(app)

from app.models import models
from app.routes import routes

if __name__ == '__main__':
    app.run()