#!/usr/bin/env python
#
# Copyright 2011-2013 Chris Baus christopher@baus.net @baus on Twitter
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
import jinja2
import oauthclient.forms
import oauthclient.models
from google.appengine.api import users


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from gaesessions import get_current_session
from gaesessions import delete_expired_sessions


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

def administrator_with_login_redirect(method):
    """Decorate with this method to restrict to site admins. Also redirect to a login page if the user
       isn't logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if user:
            if not users.is_current_user_admin():
                return self.error(403)
            else:
                return method(self, *args, **kwargs)
        else:
            self.redirect(users.create_login_url("/admin"))

    return wrapper

class Admin(webapp.RequestHandler):
    @administrator_with_login_redirect
    def get(self):
        template_values = {}
        template_values["service_formset"] = oauthclient.forms.create_service_formset()
        template = jinja_environment.get_template('admin.html')
        self.response.out.write(template.render(template_values))

    @administrator_with_login_redirect
    def post(self):
        admin_formset = oauthclient.forms.create_service_formset(self.request.POST)
        if oauthclient.forms.save_formset(admin_formset):
            self.redirect("/")
        else:
            self.redirect("/admin")

class MainHandler(webapp.RequestHandler):
    def get(self):
        twitter_service = oauthclient.models.OAuthService.get_by_key_name("twitter")
        template = None
        if twitter_service is None:
            template = jinja_environment.get_template("register_services.html")
        else:
            template = jinja_environment.get_template("signin.html")

        self.response.out.write(template.render())

class ProfileHandler(webapp.RequestHandler):
    def render_template(self, profile_saved):
        template_values = {"twitter_screen_name": self.profile.key().id_or_name(),
                           "example_data": self.profile.example_data if self.profile.example_data is not None else "",
                           "profile_saved": profile_saved}

        template = jinja_environment.get_template("profile.html")
        self.response.out.write(template.render(template_values))


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
        twitter_service = oauthclient.models.OAuthService.get_by_key_name("twitter")

        key, secret = oauthclient.retrieve_service_request_token(twitter_service.request_token_url,
                                                                 twitter_service.consumer_key,
                                                                 twitter_service.consumer_secret)
        session = get_current_session()
        if session.is_active():
            session.terminate()
        session['twitter_request_key'] = key
        session['twitter_request_secret'] = secret

        self.redirect(oauthclient.generate_authorize_url(twitter_service.authenticate_url, key))


class TwitterAuthorized(webapp.RequestHandler):
    def get(self):
        twitter_service = oauthclient.models.OAuthService.get_by_key_name("twitter")
        verifier = self.request.get("oauth_verifier")
        session = get_current_session()
        key = session.get('twitter_request_key')
        secret = session.get('twitter_request_secret')
        if key is None or secret is None:
            self.error(500)
            return

        key, secret = oauthclient.exchange_request_token_for_access_token(twitter_service.consumer_key,
                                                                          twitter_service.consumer_secret,
                                                                          twitter_service.access_token_url,
                                                                          verifier,
                                                                          key,
                                                                          secret)

        twitapi = twitter.Api(twitter_service.consumer_key,
                              twitter_service.consumer_secret,
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


class RegisterServices(webapp.RequestHandler):
    @administrator_with_login_redirect
    def get(self):
        if oauthclient.models.OAuthService.get_by_key_name("twitter") is None:
            twitter_service = oauthclient.models.OAuthService(key_name="twitter")
            twitter_service.display_name = "Twitter"
            twitter_service.request_token_url = "https://api.twitter.com/oauth/request_token"
            twitter_service.authorize_url = "https://api.twitter.com/oauth/authenticate"
            twitter_service.access_token_url = "https://api.twitter.com/oauth/access_token"
            twitter_service.authenticate_url = "https://api.twitter.com/oauth/authenticate"
            twitter_service.save()

        self.redirect("/admin")



application = webapp.WSGIApplication([('/', MainHandler),
                                      ('/registerservices', RegisterServices),
                                      ('/admin', Admin),
                                      ('/profile', ProfileHandler),
                                      ('/signin', SignInWithTwitter),
                                      ('/services/twitter/authorized', TwitterAuthorized),
                                      ('/signout', SignOut),
                                      ('/cleanup_sessions', CleanupSessions)],
                                         debug=True)

def main(): run_wsgi_app(application)

if __name__ == '__main__':
    main()
