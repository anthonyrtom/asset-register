import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "you can not guess this one"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, r"app\static\uploads")
    DOWNLOAD_FOLDER = os.path.join(basedir, r"app\static\downloads")
    MAX_CONTENT_LENGTH = 30 * 1024 * 1024

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "files.db")
    DEBUG = True
    

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL") or "sqlite://"
    WTF_CSRF_ENABLED = False
    TESTING = True
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "production.sqlite")

config = {
    'development': DevConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevConfig
}
