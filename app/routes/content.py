from app import app, db
from flask import Flask, request, jsonify
from app.models.content import Content
from youtube.upload import upload_content

@app.route('/baguette/api/v1.0/content', methods=['POST'])
def create_content():
    try:
        content = Content(
            url = request.form.get('url'),
        )
        upload_content(request.form.get('title'), content.url)

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
        content = Content.query.filter_by(id=content_id).first()
        return jsonify({'content': content.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))


@app.route('/baguette/api/v1.0/content/<content_id>', methods=['PUT'])
def update_content(content_id):
    try:
        content = Content.query.filter_by(id=content_id).first()

        url = request.form.get('url')
        content.url = url if url != None else content.url
        
        db.session.commit()
        print("Content updated content id={}".format(content.id))
        return jsonify({'content': content.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/content/<content_id>', methods=['DELETE'])
def delete_content(content_id):
    try:
        content = Content.query.filter_by(id=content_id).first()
        db.session.delete(content)
        db.session.commit()
        return "Content deleted content id={}".format(content.id), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))