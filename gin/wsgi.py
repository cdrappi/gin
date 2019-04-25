"""
WSGI config for gin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import get_wsgi_application
from django.core.wsgi
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gin.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)