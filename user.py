from __main__ import app
from app import db
from datetime import date
from flask import Flask, request, jsonify
from baguette_backend.models import user as user_model

@app.route('/baguette/api/v1.0/users', methods=['GET'])
def get_users():
    try:
        users = user_model.User.query.all()
        return jsonify({'users': [u.serialize() for u in users]}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = user_model.User.query.filter_by(id=user_id).first()
        return jsonify({'user': user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/users', methods=['POST'])
def create_user():
    username = request.form.get('username')
    y, m, d = request.form.get('date_of_birth').split('-')
    try:
        user = user_model.User(
            username = username,
            password = request.form.get('password'),
            email = request.form.get('email'),
            first_name = request.form.get('first_name'),
            last_name = request.form.get('last_name'),
            date_of_birth = date(int(y), int(m), int(d))
        )
        db.session.add(user)
        db.session.commit()
        print("User {} added user id={}".format(username, user.id))
        return jsonify({'user': user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = user_model.User.query.filter_by(id=user_id).first()
        
        username = request.form.get('username')
        user_model.username = username if username != None else user_model.username

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

@app.route('/baguette/api/v1.0/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = user_model.User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        print("User {} deleted user id={}".format(username, user.id))
    except Exception as e:
        db.session.rollback()
        return(str(e))