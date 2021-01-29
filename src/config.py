import os

class ProductionConfig:    

    DEBUG = False
    TESTING = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_ROUNDS = 10
    SQLALCHEMY_DATABASE_URI = "postgresql://user:secret@pg_db_container:5432/mydatabase"
     