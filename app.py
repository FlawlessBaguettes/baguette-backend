from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from baguette_backend.models import content, post, user
import user
# import email_address
import post
import content

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run()