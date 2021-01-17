import os
import flask
import requests
import http.client
import httplib2
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
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
#     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
	http.client.IncompleteRead, http.client.ImproperConnectionState,
	http.client.CannotSendRequest, http.client.CannotSendHeader,
	http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

@app.route('/baguette/api/v1.0/upload_to_youtube')
def upload_to_youtube():
	if 'credentials' not in flask.session:
		return flask.redirect('authorize')

	# Load credentials from the session.
	credentials = google.oauth2.credentials.Credentials(
		**flask.session['credentials'])

	youtube = googleapiclient.discovery.build(
		API_SERVICE_NAME, API_VERSION, credentials=credentials)

	title = request.args['title'] if not None else "Sample Title"
	video = request.args['video'] if not None else ""

	body=dict(
		snippet=dict(
			title=title,
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
		media_body=MediaFileUpload(video, chunksize=-1, resumable=True)
	)
	resumable_upload(insert_request)

	# Save credentials back to session in case access token was refreshed.
	# ACTION ITEM: In a production app, you likely want to save these
	#              credentials in a persistent database instead.
	flask.session['credentials'] = credentials_to_dict(credentials)

	return "Successfully uploaded video", 201

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request):
	response = None
	error = None
	retry = 0
	print('Uploading file...')
	while response is None:
		try:
			status, response = request.next_chunk()
			if response is not None:
				if 'id' in response:
					print('Video id "%s" was successfully uploaded.' % response['id'])
				else:
					exit('The upload failed with an unexpected response: %s' % response)
		except HttpError as e:
			if e.resp.status in RETRIABLE_STATUS_CODES:
				error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
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

@app.route('/baguette/api/v1.0/authorize')
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

@app.route('/baguette/api/v1.0/oauth2callback')
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