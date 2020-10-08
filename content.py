from app import app, db
from flask import Flask, request, jsonify
from baguette_backend.models import content as content_model

@app.route('/baguette/api/v1.0/content', methods=['POST'])
def create_content():
    try:
        content = content_model.Content(
            url = request.form.get('url'),
        )
        db.session.add(content)
        db.session.commit()
        print("Content added content id={}".format(content.id))
        return jsonify({'content': content.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/content/<content_id>', methods=['GET'])
def get_content(content_id):
    try:
        content = content_model.Content.query.filter_by(id=content_id).first()
        return jsonify({'content': content.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))


@app.route('/baguette/api/v1.0/content/<content_id>', methods=['PUT'])
def update_content(content_id):
    try:
        content = content_model.Content.query.filter_by(id=content_id).first()

        contentUrl = request.form.get('url')
        content.contentUrl = contentUrl if contentUrl != None else content.contentUrl
        
        db.session.commit()
        print("Content updated content id={}".format(content.id))
        return jsonify({'content': content.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/content/<content_id>', methods=['DELETE'])
def delete_content(content_id):
    try:
        content = content_model.Content.query.filter_by(id=content_id).first()
        db.session.delete(content)
        db.session.commit()
        return "Content deleted content id={}".format(content.id), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))