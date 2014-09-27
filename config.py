# -*- coding: utf8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

FACEBOOK_APP_ID = '251477738393481'
FACEBOOK_APP_SECRET = '723ce8fda1034eaa465489362cf52b31'
    
if os.environ.get('DATABASE_URL') is None:
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
    SQLALCHEMY_DATABASE_URI = "postgresql://jan@localhost/archiver"
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5

UPLOAD_FOLDER = 'app/uploads'
FILE_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['pdf','png','jpg','jpeg','gif'])