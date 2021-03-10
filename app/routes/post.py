from flask import abort, Flask, jsonify, request
import os
from sqlalchemy.orm import aliased
from sqlalchemy import distinct, func, over
from werkzeug.utils import secure_filename

from app import app, db
from app.models.post import Post, serialize, serialize_posts, serialize_replies
from app.models.content import Content
from app.models.user import User
from app.utils.video import validate_video


@app.route('/baguette/api/v1.0/posts', methods=['GET'])
def get_posts():
    try:
        ChildPost = aliased(Post, name='child_post')
        posts = (
            db.session.query(Post, Content, User, func.count(
                ChildPost.id).over(partition_by=Post.id).label('replies'))
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
        return str(e)


@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    try:
        ChildPost = aliased(Post, name='child_post')
        post = (
            db.session.query(Post, Content, User, func.count(
                ChildPost.id).over(partition_by=Post.id).label('replies'))
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
        return str(e)


@app.route('/baguette/api/v1.0/posts/replies/<post_id>', methods=['GET'])
def get_post_replies(post_id):
    try:
        ChildPost = aliased(Post, name='child_post')
        replies = (
            db.session.query(Post, Content, User, func.count(
                ChildPost.id).over(partition_by=Post.id).label('replies'))
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
        return str(e)


@app.route('/baguette/api/v1.0/posts', methods=['POST'])
@jwt_required()
def create_post():
    try:
        # Retrieve user id from token
        current_identity = get_jwt_identity()
        user_id = current_identity["id"]
        # Retrieve and validate uploaded video
        uploaded_video = request.files['video']
        filename = secure_filename(uploaded_video.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_video(uploaded_video.stream):
                abort(400)
            # TODO: This saves, the uploaded video, instead we want to upload it to YouTube
            uploaded_video.seek(0)
            uploaded_video.save(os.path.join(
                app.config['UPLOAD_PATH'], filename))

        # TODO: Create a content record based on the URL retrieved from YouTube
        '''
        content = Content(
            url = request.form.get('url')
        )

        db.session.add(content)
        '''

        # TODO: Create the post record
        '''
        post = Post(
            parentId = request.form.get('parent_id'),
            TODO: Uncomment when content record is set
            contentId = content.id,
            title = #TODO: Add title
            userId = request.form.get('user_id'),
        )
        '''

        # TODO: Commit the Post Record to the DB
        '''
        db.session.add(post)
        db.session.commit()
        print("Post added post id={}".format(post.id))
        return jsonify({'post': post.serialize()}), 201
        '''

        return "Successfully uploaded video", 201
    except Exception as e:
        return str(e)


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
        return str(e)


@app.route('/baguette/api/v1.0/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post = Post.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return "Post deleted post id={}".format(post.id), 201
    except Exception as e:
        db.session.rollback()
        return str(e)
