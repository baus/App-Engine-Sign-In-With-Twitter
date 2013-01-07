import urlparse
import oauth2 as oauth

# Request the request token from the Service Provider. Unless the consumer_key and/or secret
# the service should provide the request token with out error.
def retrieve_service_request_token(request_token_url, consumer_key, consumer_secret):
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, "GET")
    if resp.status != 200:
        raise Exception("OAuth server provided error when retrieving oauth token: %s." % resp['status'] )

    request_token = dict(urlparse.parse_qsl(content))
    return request_token['oauth_token'], request_token['oauth_token_secret']


def generate_authorize_url(authorize_url, request_token):
    return "%s?oauth_token=%s" % (authorize_url, request_token)


def exchange_request_token_for_access_token(consumer_key,
                                       consumer_secret,
                                       access_token_url,
                                       verifier,
                                       request_token_key,
                                       request_token_secret):

    request_token = oauth.Token(request_token_key,
                                request_token_secret)

    request_token.set_verifier(verifier)

    consumer = oauth.Consumer(consumer_key, consumer_secret)

    client = oauth.Client(consumer, request_token)
    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    return access_token['oauth_token'], access_token['oauth_token_secret']