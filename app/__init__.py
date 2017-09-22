import hashlib
from flask import request
from flask import jsonify
from flask import abort
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired

# import configurations file
from instance.config import configurations

# initialize sql-alchemy
db = SQLAlchemy()


def create_instance_of_flask_api(config_mode):
    from app.models import User
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

    @flask_api.route('/user/register/', methods=['POST'])
    def create_user():
        # Create a user account with the credentials provided
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', ''))

        password_hash = sha1_hash(pword)
        new_user = User(username=username, password_hash=password_hash)
        new_user.save()
        response = {
            "message": "user {} has been created successfully".format(username)
        }, 201

        return response

    @flask_api.route('/shoppinglist/', methods=['POST', 'GET'])
    def shoppinglists():

        if request.method == 'POST':
            # Create a shoppinglist with title provided
            title = str(request.data.get('title', ''))
            if title:
                shopping_list = Shoppinglists(title=title)
                shopping_list.save()
                response = jsonify(
                    {
                      'id': shopping_list.id,
                      'title': shopping_list.title
                    }
                )
                response.status_code = 201
        else:
            shopping_lists = Shoppinglists.get_all()
            results = []

            for shopping_list in shopping_lists:
                list_details = {
                    'id': shopping_list.id,
                    'title': shopping_list.title
                }
                results.append(list_details)
            response = jsonify(results)
            response.status_code = 200

        return response

    @flask_api.route('/shoppinglist/<int:list_id>',
                     methods=['PUT', 'GET', 'DELETE'])
    def shoppinglist(list_id):

        shopping_list = Shoppinglists.query.filter_by(id=list_id).first()
        if not shopping_list:
            abort(404)

        if request.method == 'PUT':
            title = str(request.data.get('title', ''))
            shopping_list.title = title
            shopping_list.save()

            response = jsonify({
                'id': shopping_list.id,
                'title': shopping_list.title
            })
            response.status_code = 200

        if request.method == 'GET':

            # retrieve the list with the id provided
            list_details = {
                'id': shopping_list.id,
                'title': shopping_list.title
            }

            response = jsonify(list_details)
            response.status_code = 200

        if request.method == 'DELETE':
            shopping_list.delete()
            response = {
                "message": "shoppinglist {} has been deleted "
                           "successfully".format(list_id)
            }, 200

        return response

    return flask_api


def sha1_hash(value):
    """Calculates the SHA1 has of a string

            :arg:
                value (str): String to be hashed

            :return
                (str): SHA1 hash
        """

    # add salt to the value
    salt = "!@3`tHy:'hj6^&7m4qG9[6"
    salted_value = value + salt

    # convert string to bytes
    value = str.encode(salted_value)

    # calculate a SHA1 hash
    hash_object = hashlib.sha1(value)
    hashed_value = hash_object.hexdigest()
    return hashed_value



