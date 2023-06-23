from django.apps import AppConfig

class SchedappConfig(AppConfig):
    '''
    The one and only app for this project (probably)
    '''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedapp'
