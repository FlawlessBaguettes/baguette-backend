from app import app, db
from flask import Flask, request, jsonify
from app.models.post import Post
from app.models.content import Content
from app.models.user import User


def serialize(post, content, user):
    return {
        'id': post.id,
        "parentId": post.parentId,
        'contentId': post.contentId,
        'userId': post.userId,
        'createdAt': post.createdAt,
        'updatedAt': post.updatedAt,
        'deletedAt': post.deletedAt,
        'url': content.url,
        'username': user.username 
    }

@app.route('/baguette/api/v1.0/posts', methods=['GET'])
def get_posts():
    try:
        posts = db.session.query(Post, Content, User).join(Content, Content.id == Post.contentId).join(User, User.id == Post.userId).all()
        return jsonify({'posts': [serialize(p[0], p[1], p[2]) for p in posts]}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        post = db.session.query(Post, Content, User).filter_by(id=post_id).join(Content, Content.id == Post.contentId).join(User, User.id == Post.userId).first()
        return jsonify({'post': serialize(post[0], post[1], post[2])}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts', methods=['POST'])
def create_post():
    try:
        content = Content(
            url = request.form.get('url')
        )

        db.session.add(content)

        post = Post(
            parentId = request.form.get('parent_id'),
            contentId = content.id,
            userId = request.form.get('user_id'),
        )
        db.session.add(post)
        db.session.commit()
        print("Post added post id={}".format(post.id))
        return jsonify({'post': post.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    try:
        post = Post.query.filter_by(id=post_id).first()
        
        parentId = request.form.get('parent_id')
        post.parentId = parentId if parentId != None else post.parentId

        contentId = request.form.get('content_id')
        post.contentId = contentId if contentId != None else post.contentId

        userId = request.form.get('user_id')
        post.userId = userId if userId != None else post.userId
        
        db.session.commit()
        
        print("Post updated post id={}".format(post.id))
        return jsonify({'post': post.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post = Post.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return "Post deleted post id={}".format(post.id), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))