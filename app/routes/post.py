from flask import abort, Flask, jsonify, request
import os
from sqlalchemy.orm import aliased
from sqlalchemy import distinct, func, over
from werkzeug.utils import secure_filename
import vimeo

from app import app, db
from app.models.post import Post, serialize, serialize_posts, serialize_replies
from app.models.content import Content
from app.models.user import User
from app.utils.video import validate_video

from flask_jwt_extended import jwt_required, get_jwt_identity

VIMEO_CLIENT = vimeo.VimeoClient(
    token='29b2d3f5fcbbf63d8f966f7c85973fe5',
    key='cd8615a35359c7d8bd60bb9766a9e9a80aa1ef01',
    secret='Xy1iTA658MNPtM8AjOezNafd33kaQx7s/Lw3rO5u8Swh6+xH1nsqCnO5eTt093n0y20kJc0mo/jEgWM/MxKjWH1wNc4zu/7VSyfbR55C4mWaEQvqvDvGm7Ay4EuVK/A4'
)


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
@jwt_required(optional=True)
def create_post():
    try:
        # Retrieve and validate uploaded video
        userRequest = request.get_json()
        print("userRequest: " + str(userRequest))
        uploaded_video = userRequest['video']
        print("uploaded video: " + str(uploaded_video))
        filename = secure_filename(uploaded_video['filename'])
        print("filename: " + str(filename))
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_video(uploaded_video.stream):
                abort(400)

            uploaded_video.seek(0)
            video_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            uploaded_video.save(video_path)

            title = userRequest['title'] or 'Untitled'
            print("title: " + title)
            print("Video title: {}".format(title))
            print("Video path: {}".format(video_path))

            uri_response = VIMEO_CLIENT.upload(video_path, data={
                'name': title,
                'description': 'Video uploaded by Flawless Baguettes'
            })

            # URI response provided in the form of /videos/<external_id> (e.g. /videos/520857963)
            uri = uri_response.split('/')[-1]
            print('Your video URI is: {}'.format(uri))

            link_response = VIMEO_CLIENT.get(
                uri_response + '?fields=link').json()
            video_link = link_response['link']
            print("Your video link is: {}".format(video_link))

            # Create a content record based on the URL retrieved from Vimeo
            content = Content(
                url=video_link,
                external_id=uri
            )
            db.session.add(content)
            db.session.commit()

            # Retrieve user id from token
            current_identity = get_jwt_identity()
            user_id = current_identity["id"]
            print("Creating a new post for the user: {}".format(user_id))

            # Create the post record
            post = Post(
                parentId=request.form.get('parent_id'),
                contentId=content.id,
                title=title,
                userId=user_id,
            )

            # TODO: Commit the Post Record to the DB
            db.session.add(post)
            db.session.commit()
            print("Post added post id={}".format(post.id))
            return jsonify({'post': post.serialize()}), 201
    except Exception as e:
        return jsonify({'msg': "error: " + str(e)}), 400


@ app.route('/baguette/api/v1.0/posts/<post_id>', methods=['PUT'])
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


@ app.route('/baguette/api/v1.0/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post = Post.query.filter_by(id=post_id).first()
        db.session.delete(post)
        db.session.commit()
        return "Post deleted post id={}".format(post.id), 201
    except Exception as e:
        db.session.rollback()
        return str(e)
