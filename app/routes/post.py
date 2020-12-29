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

###

import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from googleapiclient.http import MediaFileUpload

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl', "https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'cbE3o9GN9bjmBbh2HLLnSl0Q'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

YOUTUBE_URL_SEGMENT = "https://www.youtube.com/watch?v="
 
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
        return str(e)

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
        return str(e)

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
        return str(e)

@app.route('/baguette/api/v1.0/posts', methods=['POST'])
def create_post():
    try:
        # Retrieve and validate uploaded video
        uploaded_video = request.files['video']
        filename = secure_filename(uploaded_video.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or file_ext != validate_video(uploaded_video.stream):
                abort(400)
            # TODO: This saves, the uploaded video, instead we want to upload it to YouTube
            
            uploaded_video.seek(0)
            video_path = os.path.join(app.config['UPLOAD_PATH'], filename)
            uploaded_video.save(video_path)

            youtube_upload = flask.url_for("upload_to_youtube", _external=True)
            flask.redirect(youtube_upload)

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

@app.route('/upload_to_youtube', methods=["GET", "POST"])
def upload_to_youtube():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  youtube = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  body=dict(
    snippet=dict(
      title="My Video",
      description="Video uploaded by Flawless Baguettes",
      tags=["Flawless, Baguettes"],
      categoryId="22"
    ),
    status=dict(
      privacyStatus="private"
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=','.join(list(body.keys())),
    body=body,
    media_body=MediaFileUpload("uploads/767DC8EE-0379-415B-9BAD-2B251B1BFEBF.mov", chunksize=-1, resumable=True)
  )
  response = insert_request.execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(**response)

@app.route('/authorize', methods=["GET", "POST"])
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)

@app.route('/oauth2callback', methods=["GET", "POST"])
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('upload_to_youtube'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}