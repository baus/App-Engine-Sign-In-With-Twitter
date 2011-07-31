#!/usr/bin/env python
#
# Copyright 2011 Chris Baus christopher@baus.net @baus on Twitter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This is a short example program which shows how to use Twitter's
# "Sign In With Twitter" authentication with Google App Engine.
#
# See README.markdown
#
import os
import twitter
import oauthclient
import functools
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from gaesessions import get_current_session
from gaesessions import delete_expired_sessions
from twitteroauthkeys import TWITTER_CONSUMER_KEY
from twitteroauthkeys import TWITTER_CONSUMER_SECRET

TWITTER_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
TWITTER_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
TWITTER_AUTHENTICATE_URL = "https://api.twitter.com/oauth/authenticate"

class Profile(db.Model):
    twitter_access_token_key = db.StringProperty()
    twitter_access_token_secret = db.StringProperty()
    example_data = db.StringProperty()

def authenticated(method):
    """Decorate request handlers with this method to restrict to access to authenticated users."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        session = get_current_session()
        twitter_screen_name = session.get("twitter_screen_name")
        if twitter_screen_name is None:
            self.error(403)
            return

        self.profile = Profile.get_by_key_name(twitter_screen_name)
        if self.profile is None:
            self.profile = Profile(key_name = twitter_screen_name)
            self.profile.save()
                
        return method(self, *args, **kwargs)
    return wrapper


class MainHandler(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/signin.html')
        self.response.out.write(template.render(path, None))

class ProfileHandler(webapp.RequestHandler):
    def render_template(self, profile_saved):
        template_values = {"twitter_screen_name": self.profile.key().id_or_name(),
                               "example_data": self.profile.example_data if self.profile.example_data is not None else "",
                               "profile_saved": profile_saved}

        path = os.path.join(os.path.dirname(__file__), 'templates/profile.html')
        self.response.out.write(template.render(path, template_values))


    @authenticated
    def get(self):
        return self.render_template(False)

    @authenticated
    def post(self):
        self.profile.example_data = self.request.get("example_data")
        self.profile.save()

        return self.render_template(True)

class SignInWithTwitter(webapp.RequestHandler):
    def get(self):
        key, secret = oauthclient.RetrieveServiceRequestToken(TWITTER_REQUEST_TOKEN_URL,
                                                              TWITTER_CONSUMER_KEY,
                                                              TWITTER_CONSUMER_SECRET)
        session = get_current_session()
        if session.is_active():
            session.terminate()
        session['twitter_request_key'] = key
        session['twitter_request_secret'] = secret

        self.redirect(oauthclient.GenerateAuthorizeUrl(TWITTER_AUTHENTICATE_URL, key))


class TwitterAuthorized(webapp.RequestHandler):
    def get(self):
        verifier = self.request.get("oauth_verifier")
        session = get_current_session()
        key = session.get('twitter_request_key')
        secret = session.get('twitter_request_secret')
        if key is None or secret is None:
            self.error(500)
            return

        key, secret = oauthclient.ExchangeRequestTokenForAccessToken(TWITTER_CONSUMER_KEY,
                                                                     TWITTER_CONSUMER_SECRET,
                                                                     TWITTER_ACCESS_TOKEN_URL,
                                                                     verifier,
                                                                     key,
                                                                     secret)

        twitapi = twitter.Api(TWITTER_CONSUMER_KEY,
                              TWITTER_CONSUMER_SECRET,
                              key,
                              secret,
                              cache=None)

        twituser = twitapi.VerifyCredentials()
        profile = Profile.get_by_key_name(twituser.screen_name)
        if profile is None:
            profile = Profile(key_name=twituser.screen_name)

        profile.twitter_access_token_key = key
        profile.twitter_access_token_secret = secret
        profile.save()
        session["twitter_screen_name"] = twituser.screen_name
        self.redirect("/profile")


class SignOut(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        self.redirect("/")

class CleanupSessions(webapp.RequestHandler):
    def get(self):
        while not delete_expired_sessions():
            pass


application = webapp.WSGIApplication([('/', MainHandler),
                                      ('/profile', ProfileHandler),
                                      ('/signin', SignInWithTwitter),
                                      ('/twitterauthorized', TwitterAuthorized),
                                      ('/signout', SignOut),
                                      ('/cleanup_sessions', CleanupSessions)],
                                         debug=True)

def main(): run_wsgi_app(application)

if __name__ == '__main__':
    main()
