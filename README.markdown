# Sign In with Twitter OAuth Example #

## Try it! ##

For a live example of this example running on Google App Engine, go to [Sign In With Twitter](https://signinwithtwitter.appspot.com/).

## Overview ##

One of the great things about Google App Engine is that it has builtin authentication. The drawback is that
App Engine only supports Google authentication with experimental support for OpenId. For many applications which
closely integrate with other platforms like Twitter or Facebook, this can be less than optimal. For this reason
I created a sample application which shows how to use App Engine with Twitter's
[Sign In With Twitter](https://dev.twitter.com/docs/auth/sign-in-with-twitter) functionality.

## Dependencies ##

For convenience, the dependencies of the application are included. App Engine requires that all the application
code be bundled, so this simplifies deployment.

[httplib2](http://code.google.com/p/httplib2/)

[gae-sessions](https://github.com/dound/gae-sessions)

[python-twitter](http://code.google.com/p/python-twitter/)

[python-oauth2](https://github.com/simplegeo/python-oauth2)

## Twitter App Configuration ##

Configure your twitter app's callback URL using the following scheme: https://my-app-name.appspot.com/servcies/twitter/authorized

## Support for multiple OAuth Services ##

I'm working on extending the example to support multiple OAuth services. Dropbox will likely be the next supported
service. This brings up some interesting questions and issues around profile conflicts.

Let's say an app allows users to login with Twitter and Dropbox which are both OAuth 1.0 providers. The first time a 
new user comes to the site he logs in using his Twitter account and profile is created which links to his Twitter account. 
The next time the user comes to the site, he logs in with Dropbox, so new account is created with new profile. There is no 
way to determine this is the same user. 






