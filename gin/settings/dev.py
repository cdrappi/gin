from gin.settings import *

SECURE_SSL_REDIRECT = False

DATABASES = {'default': dj_database_url.config(default='postgres://christiandrappi@localhost:5432/gin')}
