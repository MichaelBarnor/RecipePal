from django.apps import AppConfig

class ProfileSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profileSystem'

    def ready(self):
        import profileSystem.signals
