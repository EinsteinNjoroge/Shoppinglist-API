from flask import request
from flask import jsonify
from flask import abort
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# import configurations file
from instance.config import configurations

# initialize sql-alchemy
db = SQLAlchemy()


def create_instance_of_flask_api(config_mode):
    from app.models import Shoppinglists
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

    @flask_api.route('/shoppinglist/', methods=['POST', 'GET'])
    def shoppinglists():

        if request.method == 'POST':
            # Create a shoppinglist with title provided
            title = str(request.data.get('title', ''))
            if title:
                shoppinglist = Shoppinglists(title=title)
                shoppinglist.save()
                response = jsonify(
                    {
                      'id': shoppinglist.id,
                      'title': shoppinglist.title
                    }
                )
                response.status_code = 201
        else:
            shopping_lists = Shoppinglists.get_all()
            results = []

            for shoppinglist in shopping_lists:
                list_details = {
                    'id': shoppinglist.id,
                    'title': shoppinglist.title
                }
                results.append(list_details)
            response = jsonify(results)
            response.status_code = 200

        return response

    return flask_api


