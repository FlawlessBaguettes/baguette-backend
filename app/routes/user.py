from app import app, db
from datetime import date
from flask import Flask, request, jsonify
from app.models.user import User
from app.utils.authentication import createToken, hashPassword, validatePassword
import jwt


@app.route('/baguette/api/v1.0/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify({'users': [u.serialize() for u in users]}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))


@app.route('/baguette/api/v1.0/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        return jsonify({'user': user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))


@app.route('/baguette/api/v1.0/signup', methods=['POST'])
def create_user():

    userRequest = request.get_json()
    y, m, d = userRequest['date_of_birth'].split('T')[0].split('-')
    hashedPassword = hashPassword(userRequest['password'])

    try:
        user = User(
            username=userRequest['username'],
            password=hashedPassword,
            email=userRequest['email'],
            first_name=userRequest['first_name'],
            last_name=userRequest['last_name'],
            date_of_birth=date(int(y), int(m), int(d))
        )
        db.session.add(user)
        db.session.commit()
        print("User {} added user id={}".format(user.username, user.id))

        userData = {
            "username": user.username,
            "id": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name
        }
        token = createToken(userData)
        decodedToken = jwt.decode(
            token, app.config["SECRET_KEY"], algorithms="HS256")
        expiryTime = decodedToken["exp"]

        return jsonify({
            "token": token,
            "expiryTime": expiryTime,
            "userData": userData
        }), 201

    except Exception as e:
        db.session.rollback()
        return(str(e))


@ app.route('/baguette/api/v1.0/auth', methods=['POST'])
def auth_user():
    userRequest = request.get_json()
    email = userRequest['email']
    password = userRequest['password']

    try:
        user = User.query.filter_by(email=email).first()
        if user is None:
            return "User doesn't exist"

        isPasswordValid = validatePassword(password, user.password)

        if isPasswordValid is False:
            return "Incorrect password"

        userData = {
            "username": user.username,
            "id": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name
        }
        token = createToken(userData)
        decodedToken = jwt.decode(
            token, app.config["SECRET_KEY"], algorithms="HS256")
        expiryTime = decodedToken["exp"]

        return jsonify({
            "token": token,
            "expiryTime": expiryTime,
            "userData": userData
        }), 201

    except Exception as e:
        db.session.rollback()
        return(str(e))


@ app.route('/baguette/api/v1.0/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()

        username = request.form.get('username')
        user.username = username if username != None else user.username

        password = request.form.get('password')
        user.password = password if password != None else user.password

        email = request.form.get('email')
        user.email = email if email != None else user.email

        first_name = request.form.get('first_name')
        user.first_name = first_name if first_name != None else user.first_name

        last_name = request.form.get('last_name')
        user.last_name = last_name if last_name != None else user.last_name

        date_of_birth = request.form.get('date_of_birth')
        if date_of_birth != None:
            y, m, d = request.form.get('date_of_birth').split('-')
            user.date_of_birth = date(int(y), int(m), int(d))
        else:
            user.date_of_birth = user.date_of_birth

        db.session.commit()

        print("User {} updated user id={}".format(username, user.id))
        return jsonify({'user': user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))


@ app.route('/baguette/api/v1.0/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        print("User {} deleted user id={}".format(user.username, user.id))
    except Exception as e:
        db.session.rollback()
        return(str(e))
