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

# When running locally, disable OAuthlib's HTTPs verification.
# ACTION ITEM for developers:
#     When running in production *do not* leave this option enabled.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route('/upload_to_youtube')
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

@app.route('/authorize')
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

@app.route('/oauth2callback')
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