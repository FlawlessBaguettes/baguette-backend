# -*- coding: utf-8 -*-

import os
import flask
import requests
from app import app

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

@app.route('/test_api_request', methods=["GET", "POST"])
def test_api_request():
  print("Uploading video at path: {}".format(video_path))
  url_test = flask.url_for('authorize', _external=True)
  print("URL IS:")
  print(url_test)
  if 'credentials' not in flask.session:
    return flask.redirect(url_test)

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  youtube = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  # channel = youtube.channels().list(mine=True, part='snippet').execute()

  options = {}
  options["file"] = "uploads/767DC8EE-0379-415B-9BAD-2B251B1BFEBF.mov"
  options["keywords"] = "Flawless, Baguettes"

  tags = None
  if options["keywords"]:
    tags = options["keywords"].split(',')

  body=dict(
    snippet=dict(
      title="My Video",
      description="Video uploaded by Flawless Baguettes",
      tags=tags,
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
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting 'chunksize' equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True)
  )
  # response = insert_request.execute()
  response = resumable_upload(insert_request)

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  if response:
    return flask.jsonify(**response)
  else:
    return "Upload failed"

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print('Uploading file...')
      status, response = request.next_chunk()
      if response is not None:
        if 'id' in response:
          print('Video id "%s" was successfully uploaded.' % response['id'])
          return response
        else:
          exit('The upload failed with an unexpected response: %s' % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = 'A retriable error occurred: %s' % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit('No longer attempting to retry.')

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print('Sleeping %f seconds and then retrying...' % sleep_seconds)
      time.sleep(sleep_seconds)

@app.route('/authorize', methods=["GET", "POST"])
def authorize():
  print("AUTHORIZE CALLED")
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
  print(flask.session['state'])

  return flask.redirect(authorization_url)


@app.route('/oauth2callback', methods=["GET", "POST"])
def oauth2callback():
  print("OAUTH CALLED")
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

  return flask.redirect(flask.url_for('test_api_request'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}