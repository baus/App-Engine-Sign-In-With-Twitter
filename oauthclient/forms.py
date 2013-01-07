import django.forms

class ServiceForm(django.forms.Form):
    display_name = django.forms.CharField()
    consumer_secret = django.forms.CharField()
    consumer_key = django.forms.CharField()
    request_token_url = django.forms.URLField(initial='http://')
    authorize_url = django.forms.URLField(initial='http://')
    access_token_url = django.forms.URLField(initial='http://')

