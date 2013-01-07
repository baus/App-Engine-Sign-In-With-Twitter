import datastore
import oauthclient

def get_user_service_token(profile, service_id):
    for token in profile.oauth_tokens:
        if token.oauth_service.id == service_id:
            return token

    return None

def authorize_service(serviceId, userId):
    profile = datastore.get_profile_by_handle(userId)
    token = get_user_service_token(profile, serviceId)
    if token and datastore.IsAccessToken(token):
        # Already have access token. Nothing to do.
        return


    service = datastore.OAuthService.all().filter("id =", serviceId).get()
    if not service:
        # Service not found. Could potentially throw here.
        return

    key, secret = oauthclient.retrieve_service_request_token(service.request_token_url,
                                                          service.consumer_key,
                                                          service.consumer_secret)

    token = datastore.OAuthToken() if not token else token

    token.profile = profile
    token.token_type = 'request'
    token.oauth_key = key
    token.secret = secret
    token.oauth_service = service
    token.save()
    return oauthclient.generate_authorize_url(service.authorize_url, key)


def service_authorized(serviceId, userId, oauth_verifier):
    profile = datastore.get_profile_by_handle(userId)

    if not profile:
        raise Exception("Profile %s not found" % userId)

    token = get_user_service_token(profile, serviceId)
    if not datastore.IsRequestToken(token):
        raise Exception("Request token not found")

    service = token.oauth_service

    key, secret = oauthclient.exchange_request_token_for_access_token(service.consumer_key,
                                                                 service.consumer_secret,
                                                                 service.access_token_url,
                                                                 oauth_verifier,
                                                                 token.oauth_key,
                                                                 token.secret)
    token.token_type = 'access'
    token.oauth_key = key
    token.secret = secret
    token.save()
