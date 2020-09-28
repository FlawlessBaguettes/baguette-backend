from flask import Flask

app = Flask(__name__)

import users
import email_address
import post
import content

@app.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)