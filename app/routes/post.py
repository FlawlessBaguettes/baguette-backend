from flask import abort, Flask, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
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
        # Retrieve and validate uploaded video
        uploaded_video = request.files['video']
        filename = secure_filename(uploaded_video.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_video(uploaded_video.stream):
                abort(400)

            vimeo_client = app.config["VIMEO_CLIENT"]
            video_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            title = request.form.get('title') or 'Untitled'

            upload_response = vimeo_client.upload(video_path, data={
                'name': title,
                'description': 'Video uploaded by Flawless Baguettes'
            })

            # Upload response provided in the form of /videos/<external_id> (e.g. /videos/520857963)
            vimeo_id = upload_response.split('/')[-1]

            link_response = vimeo_client.get(upload_response + '?fields=link').json()
            video_link = link_response['link']

            # Create a content record based on the URL retrieved from Vimeo
            content = Content(
                url = video_link,
                external_id = vimeo_id
            )
            db.session.add(content)
            db.session.commit()

            # Retrieve user id from token
            current_identity = get_jwt_identity()
            user_id = current_identity["id"]

            parent_id = request.form.get('parent_id')

            # Create the post record
            post = Post(
                parentId = parent_id,
                contentId = content.id,
                title = title,
                userId = user_id,
            )
            db.session.add(post)
            db.session.commit()
            print("Post added post id={}".format(post.id))
            return jsonify({'post': post.serialize()}), 201
    except Exception as e:
        print(str(e))
        return jsonify({"message": "Sorry, something went wrong while uploading your video. Please try again later."}), 400


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
