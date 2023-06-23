"""
WSGI config for schedris project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schedris.settings')
os.environ['DJANGO_SETTINGS_MODULE'] = 'schedris.settings'

# Not sure if this is still necessary or not, but an older post about django security
# here https://security.stackexchange.com/questions/8964/trying-to-make-a-django-based-site-use-https-only-not-sure-if-its-secure
# said to set it, and it shoudn't be hurting anything.
# The rest of the suggestions seemed to be in line with the current way django security works
# so we have included this one too for good measure.
os.environ['HTTPS'] = "on"

application = get_wsgi_application()
