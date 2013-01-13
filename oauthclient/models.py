from google.appengine.ext import db

class OAuthService(db.Model):
    display_name = db.StringProperty()
    consumer_secret = db.StringProperty()
    consumer_key = db.StringProperty()
    request_token_url = db.StringProperty()
    authorize_url = db.StringProperty()
    access_token_url = db.StringProperty()
    authenticate_url = db.StringProperty()

class Profile(db.Model):
    create_date = db.DateTimeProperty(auto_now_add=True)

class OAuthToken(db.Model):
    oauth_service = db.ReferenceProperty(OAuthService)
    timestamp = db.DateTimeProperty(auto_now=True)
    oauth_key = db.StringProperty()
    secret = db.StringProperty()
    token_type = db.StringProperty(choices=['request', 'access'])
    profile = db.ReferenceProperty(Profile, collection_name="oauth_tokens")

def get_profile_by_handle(screen_name):
    return Profile.get_by_key_name(screen_name)


def is_request_token(token):
    return (token and token.token_type == 'request' and
            token.secret and len(token.secret) > 0 and
            token.oauth_key and len(token.oauth_key) > 0)

def is_access_token(token):
    return (token and token.token_type == 'access' and
            token.secret and len(token.secret) > 0 and
            token.oauth_key and len(token.oauth_key) > 0)



