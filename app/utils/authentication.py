import jwt
import bcrypt
import config
import datetime


def createToken(user):
    try:
        # print(app.config["SECRET_KEY"])
        if (user["username"] is None or user["id"] is None):
            raise ValueError("user object passed to createToken is malformed")

    except Exception as e:
        print("Error: " + str(e))

    print("string passed to createToken: " + str(user))

    token = jwt.encode({
        "id": user["id"],
        "username": user["username"],
        # "iss": "api.baguette",
        # "aud": "api.baguette",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=900),
    },
        "temp-secret",
        algorithm="HS256"
    )
    print("token is: " + token)
    return token


def hashPassword(password):
    # level 12 strength hash
    salt = bcrypt.gensalt(12)
    hashed = bcrypt.hashpw(password.encode("utf8"), salt).decode("utf8")

    print("password passed to hashPassword function: " + password)
    print("salt used: " + salt.decode("utf8"))
    print("hashedpassword returned by function " + hashed)
    return hashed


def verifyPassword(passwordAttempt, hashedPassword):
    print("passwordAttemp is: " + passwordAttempt)
    print("hashed password is: " + hashedPassword)
    if bcrypt.checkpw(passwordAttempt.encode("utf8"), hashedPassword.encode("utf8")):
        return True
    else:
        return False
