from app import app, db
from flask import Flask, request, jsonify
from sqlalchemy.orm import aliased
from sqlalchemy import distinct, func, over
from app.models.post import Post, serialize, serialize_posts, serialize_replies
from app.models.content import Content
from app.models.user import User
from youtube.upload import upload_content

@app.route('/baguette/api/v1.0/posts', methods=['GET'])
def get_posts():
    try:
        ChildPost = aliased(Post, name='child_post')
        posts = (
                    db.session.query(Post, Content, User, func.count(ChildPost.id).over(partition_by=Post.id).label('replies'))
                    .distinct()
                    .outerjoin(
                        (ChildPost, ChildPost.parentId == Post.id)
                    )
                    .join(
                        (Content, Content.id == Post.contentId),
                        (User, User.id == Post.userId)
                    )
                    .filter(Post.parentId == None)
                    .order_by(Post.createdAt.desc())
                ).all()

        return jsonify({'posts': serialize_posts(posts)}), 200
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        ChildPost = aliased(Post, name='child_post')
        post = (
                    db.session.query(Post, Content, User, func.count(ChildPost.id).over(partition_by=Post.id).label('replies'))
                    .distinct()
                    .outerjoin(
                        (ChildPost, ChildPost.parentId == Post.id)
                    )
                    .join(
                        (Content, Content.id == Post.contentId),
                        (User, User.id == Post.userId)
                    )
                    .filter(Post.id == post_id)
                    .order_by(Post.createdAt.desc())
                ).first()
        
        return jsonify({'post': serialize(post[0], post[1], post[2], post[3])}), 200
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts/replies/<post_id>', methods=['GET'])
def get_post_replies(post_id):
    try:
        ChildPost = aliased(Post, name='child_post')
        replies = (
                    db.session.query(Post, Content, User, func.count(ChildPost.id).over(partition_by=Post.id).label('replies'))
                    .distinct()
                    .outerjoin(
                        (ChildPost, ChildPost.parentId == Post.id)
                    )
                    .join(
                        (Content, Content.id == Post.contentId),
                        (User, User.id == Post.userId)
                    )
                    .filter(Post.parentId == post_id)
                    .order_by(Post.createdAt.desc())
                ).all()
        return jsonify({'replies': serialize_replies(replies)}), 200
    except Exception as e:
        db.session.rollback()
        return(str(e))

@app.route('/baguette/api/v1.0/posts', methods=['POST'])
def create_post():
    try:
        # TO DO: Upload video to Youtube and create content using resulting URL
        # youtube_url = upload_content(request.form.get('title'), filepath)
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