import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print "Load settings from local"

'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kkma',
        'USER': 'root',
        'PASSWORD': 'snowwhite',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
    'remote': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'kkma',
        'USER': 'kkma',
        'PASSWORD': 'qN!4AA6fFGK7XVT1GvF!^p',
        'HOST': 'mysql.nhutrinh.com',
        'PORT': '3306',
    }
}
'''