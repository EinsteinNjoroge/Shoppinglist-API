from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# import configurations file
from instance.config import configurations

# initialize sql-alchemy
db = SQLAlchemy()


def create_instance_of_flask_api(config_mode):
    """
    Instantiates Flask and sets configurations for the flask api

    Args:
        config_mode (str): Name of the preferred configuration for this instance

    Returns:
        FlaskAPI: instance of API

    """
    flask_api = FlaskAPI(__name__, instance_relative_config=True)
    flask_api.config.from_object(configurations[config_mode])
    flask_api.config.from_pyfile('config.py')
    flask_api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(flask_api)

    return flask_api


