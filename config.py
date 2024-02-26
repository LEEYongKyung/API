import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:828ll998@mydb.cme8gehziiua.ap-northeast-2.rds.amazonaws.com:3306/bswms'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'mysql+pymysql://root:!b$wms2019!$@bswms.c3cdvfcs5uix.ap-northeast-2.rds.amazonaws.com:3306/bswms'
    # BABEL_TRANSLATION_DIRECTORIES = os.getcwd() + '/translations'
    BABEL_TRANSLATION_DIRECTORIES = basedir + '/translations'


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:!b$wms2019!$@bswms.c0grph7n5f6y.ap-northeast-2.rds.amazonaws.com:3306/bswms'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'mysql+pymysql://root:!b$wms2019!$@bswms.c3cdvfcs5uix.ap-northeast-2.rds.amazonaws.com:3306/bswms'
    # BABEL_TRANSLATION_DIRECTORIES = os.getcwd() + '/translations'
    BABEL_TRANSLATION_DIRECTORIES = basedir + '/translations'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class HerokuConfig(ProductionConfig):

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


class AwsConfig(ProductionConfig):
    # MONGO_URI = os.environ.get('MONGO_URI')
    # MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'prod': ProductionConfig,
    'heroku': HerokuConfig,
    'aws': AwsConfig,

    'default': DevelopmentConfig
}
