import django.forms
import models
from django.forms.formsets import formset_factory


class ServiceForm(django.forms.Form):
    display_name = django.forms.CharField()
    consumer_secret = django.forms.CharField()
    consumer_key = django.forms.CharField()
    request_token_url = django.forms.URLField(initial='http://')
    authorize_url = django.forms.URLField(initial='http://')
    access_token_url = django.forms.URLField(initial='http://')

def create_service_formset():
    initial_values = []
    for service in models.OAuthService.all():
        service_initial_values = {}
        service_initial_values["display_name"] = service.display_name
        service_initial_values["consumer_secret"] = service.consumer_secret
        service_initial_values["consumer_key"] = service.consumer_key
        service_initial_values["request_token_url"] = service.request_token_url
        service_initial_values["authorize_url"] = service.authorize_url
        service_initial_values["access_token_url"] = service.access_token_url
        initial_values.append(service_initial_values)

    ServiceFormset = formset_factory(ServiceForm, extra=0)
    return ServiceFormset(initial = initial_values)
    
