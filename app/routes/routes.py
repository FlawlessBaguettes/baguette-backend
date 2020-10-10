from app import app
from app.routes import user
# from app.routes import email_address
from app.routes import post
from app.routes import content

@app.route('/')
def index():
    return "Hello, World!"