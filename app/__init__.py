from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# import configurations file
from instance.config import configurations

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(configuration_name):
    """
    Instantiates Flask and sets configurations for the flask app

    Args:
        configuration_name (str): Name of the preferred configuration for this instance

    Returns:
        FlaskAPI: instance of API

    """
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(configurations[configuration_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    return app
