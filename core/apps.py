from django.apps import AppConfig
from django.contrib.auth import get_user_model
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'


    # def ready(self):
    #     user_model = get_user_model()
    #     try:
    #         user_model.objects.get(username=os.getenv("ADMIN_LOGIN"))
    #     except user_model.DoesNotExist:
    #         print("createsuperuser: ", user_model.objects.create_superuser(os.getenv("ADMIN_LOGIN"), os.getenv("ADMIN_MAIL"), os.getenv("ADMIN_PASSWORD")))
