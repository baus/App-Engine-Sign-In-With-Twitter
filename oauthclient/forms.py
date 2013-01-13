import django.forms
import models
from django.forms.formsets import formset_factory


class ServiceForm(django.forms.Form):
    id = django.forms.CharField(widget=django.forms.HiddenInput())
    display_name = django.forms.CharField(required=False)
    consumer_secret = django.forms.CharField()
    consumer_key = django.forms.CharField()
    request_token_url = django.forms.URLField(initial='http://')
    authorize_url = django.forms.URLField(initial='http://')
    access_token_url = django.forms.URLField(initial='http://')

def create_service_formset(data=None):

    ServiceFormset = formset_factory(ServiceForm, extra=0)

    if data is None:
        initial_values = []
        for service in models.OAuthService.all():
            service_initial_values = {}
            service_initial_values["id"]                = service.key().name()
            service_initial_values["display_name"]      = service.display_name
            service_initial_values["consumer_secret"]   = service.consumer_secret
            service_initial_values["consumer_key"]      = service.consumer_key
            service_initial_values["request_token_url"] = service.request_token_url
            service_initial_values["authorize_url"]     = service.authorize_url
            service_initial_values["access_token_url"]  = service.access_token_url
            initial_values.append(service_initial_values)

        return ServiceFormset(initial = initial_values)

    return ServiceFormset(data)

def save_formset(service_formset):
    for form in service_formset:
        if form.is_valid():
            service = models.OAuthService.get_by_key_name(form.cleaned_data["id"])
            service.consumer_secret   = form.cleaned_data["consumer_secret"]
            service.consumer_key      = form.cleaned_data["consumer_key"]
            service.request_token_url = form.cleaned_data["request_token_url"]
            service.authorize_url     = form.cleaned_data["authorize_url"]
            service.access_token_url  = form.cleaned_data["access_token_url"]
            service.save()
            return True
        return False
