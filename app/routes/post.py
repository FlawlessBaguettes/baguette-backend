from app import app, db
from flask import Flask, request, jsonify
from sqlalchemy import or_
from sqlalchemy.orm import aliased
from app.models.post import Post, serialize, serialize_post
from app.models.content import Content
from app.models.user import User

@app.route('/baguette/api/v1.0/posts', methods=['GET'])
def get_posts():
    try:
        ParentPost = aliased(Post, name='parent_post')
        ChildPost = aliased(Post, name='child_post')
        posts = (db.session.query(ParentPost, ChildPost, Content, User)
                    .filter(ParentPost.parentId == None)
                    .outerjoin(
                        (ChildPost, ChildPost.id == ParentPost.id)
                    )
                    .join(
                        (Content, Content.id == ParentPost.contentId),
                        (User, User.id == ParentPost.userId)
                    )
                    .order_by(ParentPost.createdAt.desc())
                )
        print(posts)
        return jsonify({'posts': [serialize_post(p) for p in posts]}), 201
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        ParentPost = aliased(Post, name='parent_post')
        ChildPost = aliased(Post, name='child_post')
        post = (db.session.query(ParentPost, ChildPost, Content, User)
                    .outerjoin(
                        (ChildPost, ChildPost.id == ParentPost.id)
                    )
                    .filter(or_(ParentPost.id == post_id, ChildPost.parentId == post_id))
                    .join(
                        (Content, Content.id == ParentPost.contentId),
                        (User, User.id == ParentPost.userId)
                    )
                    .order_by(ParentPost.createdAt.asc())
                )

        return jsonify({'post': serialize_post(post)}), 201
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