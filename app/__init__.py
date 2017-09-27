import hashlib
from flask import request
from flask import jsonify
from flask import abort
from flask_api import FlaskAPI
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from instance.config import configurations  # import configurations file
from app.models import db
from app.models import secret_key
from app.models import User
from app.models import Shoppinglists
from app.models import ShoppingListItems


def launch_app(config_mode):
    flask_api = FlaskAPI(__name__, instance_relative_config=True)
    flask_api.config.from_object(configurations[config_mode])
    flask_api.config.from_pyfile('config.py')
    flask_api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_api.secret_key = secret_key
    db.init_app(flask_api)

    @flask_api.route('/user/register/', methods=['POST'])
    def create_user():
        # Create a user account with the credentials provided
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', ''))

        password_hash = sha1_hash(pword)
        new_user = User(username=username, password_hash=password_hash)
        new_user.save()
        response = jsonify({
            "message": "user `{}` has been created".format(username),
            "id": new_user.id
        })
        response.status_code = 201

        return response

    @flask_api.route('/user/login/', methods=['POST'])
    def authenticate_user():
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', ''))

        response = jsonify({
            "message": "Wrong credentials combination"
        })
        response.status_code = 401

        password_hash = sha1_hash(pword)
        user = User.query.filter_by(password_hash=password_hash).first()

        print(user.password_hash)

        if user:
            token = generate_auth_token(user).decode("utf-8")

            response = jsonify({
                "token": token
            })
            response.status_code = 200

        return response

    @flask_api.route('/shoppinglist/', methods=['POST', 'GET'])
    def shoppinglists():
        response = None

        if request.method == 'POST':
            # Create a shoppinglist with title provided
            title = str(request.data.get('title', ''))
            user_id = str(request.data.get('user_id', ''))
            if title:
                shopping_list = Shoppinglists(title=title, user_id=user_id)
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
                response = jsonify({
                    "message": "shoppinglist {} has been deleted "
                               "successfully".format(list_id)
                })
                response.status_code = 200

            return response

    @flask_api.route('/shoppinglist/<int:list_id>/items/',
                     methods=['POST', 'GET'])
    def shoppinglist_items(list_id):
        response = None

        if request.method == 'POST':
            # Create shoppinglist item with the name provided
            name = str(request.data.get('name', ''))
            if name:
                item = ShoppingListItems(name=name, shoppinglist_id=list_id)
                item.save()
                response = jsonify(
                    {
                        'id': item.id,
                        'name': item.name
                    }
                )
                response.status_code = 201
        else:
            items = ShoppingListItems.query.filter_by(shoppinglist_id=list_id)
            results = []

            for item in items:
                list_details = {
                    'id': item.id,
                    'name': item.name
                }
                results.append(list_details)
            response = jsonify(results)
            response.status_code = 200

        return response

    @flask_api.route('/shoppinglist/<int:list_id>/items/<int:item_id>',
                     methods=['PUT', 'GET', 'DELETE'])
    def shoppinglist_item(list_id, item_id):

        shopping_list = Shoppinglists.query.filter_by(id=list_id).first()
        if not shopping_list:
            abort(404)
        item = ShoppingListItems.query.filter_by(id=item_id).first()
        if not item:
            abort(404)

        if request.method == 'PUT':
            name = str(request.data.get('name', ''))
            item.name = name
            item.save()

            response = jsonify({
                'id': item.id,
                'name': item.name
            })
            response.status_code = 200

        if request.method == 'GET':
            # retrieve the list with the id provided
            list_details = {
                'id': item.id,
                'name': item.name
            }

            response = jsonify(list_details)
            response.status_code = 200

        if request.method == 'DELETE':
            item.delete()
            response = jsonify({
                "message": "item {} has been deleted "
                           "successfully".format(item_id)
            })
            response.status_code = 200

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


def generate_auth_token(user):
    s = Serializer(secret_key, expires_in=600)
    return s.dumps({'id': user.id})



