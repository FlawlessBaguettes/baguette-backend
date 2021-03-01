import jwt
import bcrypt
import datetime

from app import app


def createToken(user):
    try:
        if (user["username"] is None):
            raise ValueError("User object passed to createToken is malformed")

    except Exception as e:
        return(str(e))

    token = jwt.encode({
        "id": user["id"],
        "username": user["username"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(weeks=52),
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return token


def hashPassword(password):
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode("utf8"), salt).decode("utf8")
    return hashed


def validatePassword(passwordAttempt, hashedPassword):
    if bcrypt.checkpw(passwordAttempt.encode("utf8"), hashedPassword.encode("utf8")):
        return True
    else:
        return False
