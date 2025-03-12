from django.contrib import admin

from django.apps import apps

models = apps.get_app_config('blog').get_models()

for model in models:
    if model not in admin.site._registry:  # Check if the model is already registered
        admin.site.register(model)