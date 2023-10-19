from config.env import env

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp-mail.outlook.com"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
