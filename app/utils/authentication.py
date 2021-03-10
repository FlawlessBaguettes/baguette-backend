import bcrypt
import datetime

from app import app
from flask_jwt_extended import create_access_token


def createToken(user):

    access_token = create_access_token(identity={
        "id": user["id"],
        "username": user["username"],
    })

    return access_token


def hashPassword(password):
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode("utf8"), salt).decode("utf8")
    return hashed


def validatePassword(passwordAttempt, hashedPassword):
    if bcrypt.checkpw(passwordAttempt.encode("utf8"), hashedPassword.encode("utf8")):
        return True
    else:
        return False
