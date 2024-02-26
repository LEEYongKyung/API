from flask import Flask
# from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request
from config import config
from flask_babel import Babel
from flask_babel import gettext

from flask_socketio import SocketIO

# mongo = PyMongo()
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
socket_io = SocketIO()


@babel.localeselector
def get_locale():
    lang = 'ko'

    try:
        header = request.headers.get('BSRD-INFO')
        if header:
            headers = header.split(';')
            if len(headers) > 5:
                lang = headers[5]
    except:
        pass

    return lang.lower()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # mongo.init_app(app, config_prefix='MONGO')
    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    socket_io.init_app(app, async_mode='threading')
    # socket_io.init_app(app, async_mode='threading', cors_allowed_origins="*")

    # for test
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/Lang')
    def hello_world1():
        print(gettext('user_name_label'))
        # return render_template('index.html',
        #                        user_name='ash84')

        return gettext('user_name_label')

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db.session.remove()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
