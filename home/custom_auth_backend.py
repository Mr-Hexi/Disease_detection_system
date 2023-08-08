#custom authentication
AUTHENTICATION_BACKENDS = [
    'custom_auth_backend.AdminAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]