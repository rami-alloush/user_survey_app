from django.conf import settings

# Set limit for number of questions per quiz
QUIZ_QUESTIONS = 5
QUIZ_DURATION_MINUTES = 60
PASS_SCORE = 3
COURSE_ATTEMPTS = 3

# Email Settings (should go to Project settings.py)

# For Gmail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'email@gmail.com'
# EMAIL_HOST_PASSWORD = 'password'

# For local SMTP Sever (by running: python -m smtpd -n -c DebuggingServer localhost:1025)
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False
# DEFAULT_FROM_EMAIL = 'testing@example.com'


# For sendgrid.net
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'sendgrid_username'
# EMAIL_HOST_PASSWORD = 'sendgrid_password'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
