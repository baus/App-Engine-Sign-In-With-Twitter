from gaesessions import SessionMiddleware

def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key="signinwithtwittertestapp_signinwithtwittertestapp_signinwithtwittertestapp_foobar", cookie_only_threshold=0)
    return app
