import hashlib
import os
from flask import request
from flask import jsonify
from flask_api import FlaskAPI
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
from itsdangerous import SignatureExpired
from instance.config import configurations  # import configurations file
from app.models import db
from app.models import User
from app.models import Shoppinglists
from app.models import ShoppingListItems

secret_key = os.urandom(24)  # create a random secret key for the application
user_logged_in = None


def launch_app(config_mode):
    flask_api = FlaskAPI(__name__, instance_relative_config=True)
    flask_api.config.from_object(configurations[config_mode])
    flask_api.config.from_pyfile('config.py')
    flask_api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_api.secret_key = secret_key
    db.init_app(flask_api)
    auth = HTTPBasicAuth()

    @flask_api.route('/user/register/', methods=['POST'])
    def create_user():
        # Create a user account with the credentials provided
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', '')).lower().strip()

        if not username or not pword:
            response = jsonify({
                "error_msg": "Please provide a valid username and password"
            })
            response.status_code = 400

        elif len(pword) < 7:
            response = jsonify({
                "error_msg": "password must be at-least 6 characters long"
            })
            response.status_code = 409

        # Check username is already registered
        elif User.query.filter_by(username=username).first():
            response = jsonify({
                "error_msg": "username `{}` is already registered. Please "
                             "provide a unique username".format(username)
            })
            response.status_code = 409

        else:
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

        if not username or not pword:
            response = jsonify({
                "error_msg": "Please provide a valid username and password"
            })
            response.status_code = 400

        elif verify_password(username, pword):
            token = generate_auth_token(user_logged_in)
            response = jsonify({
                "token": token.decode('ascii')
            })
            response.status_code = 200

        else:
            response = jsonify({
                "message": "Wrong credentials combination"
            })
            response.status_code = 401

        return response

    @auth.verify_password
    def verify_password(username, pword):
        # Attempt to authenticate using token
        user = verify_auth_token(username)

        if not user:
            # attempt authentication using password
            password_hash = sha1_hash(pword)
            user = User.query.filter_by(username=username,
                                        password_hash=password_hash).first()
        if user:
            global user_logged_in
            user_logged_in = user
            return True
        return False

    @flask_api.route('/shoppinglist/', methods=['POST', 'GET'])
    @auth.login_required
    def shoppinglists():

        user_id = user_logged_in.id
        shopping_lists = None
        limit = None

        if request.method == 'POST':

            # Create a shoppinglist with title provided
            title = str(request.data.get('title', '')).lower().strip()

            error_message = validate_title(title)
            if error_message:
                return error_message

            else:
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
            # check if a search keyword has been provided
            args = request.args
            if args:
                if 'limit' in args:
                    # limit number of results returned
                    limit = int(args['limit'])

                if 'q' in args:
                    # search for shoppinglists that contain keyword provided
                    keyword = str(args['q']).lower()

                    if limit:
                        shopping_lists = Shoppinglists.query.filter(
                            Shoppinglists.title.like("%{}%".format(keyword)),
                            Shoppinglists.user_id == user_id
                        ).limit(limit).all()
                    else:
                        shopping_lists = Shoppinglists.query.filter(
                            Shoppinglists.title.like("%{}%".format(keyword)),
                            Shoppinglists.user_id == user_id
                        ).all()

                    if len(shopping_lists) < 1:
                        response = jsonify({
                            'error_msg': "There is no shoppinglist that matches"
                                         " the keyword `{}`.".format(keyword)
                        })
                        response.status_code = 404
                        return response

            if not shopping_lists:
                if limit:
                    # Limit number of shoppinglists returned
                    shopping_lists = Shoppinglists.query.filter_by(
                        user_id=user_id).limit(limit)
                else:
                    # Retrieve all shoppinglists
                    shopping_lists = Shoppinglists.query.filter_by(
                        user_id=user_id).all()

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
    @auth.login_required
    def shoppinglist(list_id):
        user_id = user_logged_in.id

        # check if shoppinglist with id <list_id> exists
        shopping_list = Shoppinglists.query.filter_by(id=list_id,
                                                      user_id=user_id).first()
        if not shopping_list:
            response = jsonify({
                'error_msg': "Requested shoppinglist was not found"
            })
            response.status_code = 404
            return response

        if request.method == 'PUT':
            title = str(request.data.get('title', '')).lower().strip()

            error_message = validate_title(title)
            if error_message:
                return error_message

            shopping_list.title = title
            shopping_list.save()

            response = jsonify({
                'id': shopping_list.id,
                'title': shopping_list.title
            })
            response.status_code = 200

        elif request.method == 'DELETE':

            shopping_list.delete()
            response = jsonify({
                "message": "shoppinglist {} has been deleted "
                           "successfully".format(list_id)
            })
            response.status_code = 200

        else:
            # retrieve the list with the id provided
            list_details = {
                'id': shopping_list.id,
                'title': shopping_list.title
            }

            response = jsonify(list_details)
            response.status_code = 200

        return response

    @flask_api.route('/shoppinglist/<int:list_id>/items/',
                     methods=['POST', 'GET'])
    @auth.login_required
    def shoppinglist_items(list_id):

        user_id = user_logged_in.id
        shopping_list = Shoppinglists.query.filter_by(id=list_id,
                                                      user_id=user_id).first()
        if not shopping_list:
            response = jsonify({
                'error_msg': "Requested shoppinglist was not found"
            })
            response.status_code = 404
            return response

        if request.method == 'POST':
            # Create shoppinglist item with the name provided
            name = str(request.data.get('name', '')).lower().strip()

            error_message = validate_item_name(name, list_id)

            if error_message:
                return error_message

            else:
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
            # check if a search keyword has been provided
            args = request.args
            if not args:
                items = ShoppingListItems.query.filter_by(
                    shoppinglist_id=list_id)
            else:
                # search for item that contain keyword provided
                keyword = str(args['q']).lower()
                items = ShoppingListItems.query.filter(
                    ShoppingListItems.name.like("%{}%".format(keyword)),
                    ShoppingListItems.shoppinglist_id == list_id
                ).all()

                if len(items) < 1:
                    response = jsonify({
                        'error_msg': "No item matches"
                                     " the keyword `{}`.".format(keyword)
                    })
                    response.status_code = 404
                    return response

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
    @auth.login_required
    def shoppinglist_item(list_id, item_id):

        user_id = user_logged_in.id
        shopping_list = Shoppinglists.query.filter_by(id=list_id,
                                                      user_id=user_id).first()
        item = ShoppingListItems.query.filter_by(
            id=item_id, shoppinglist_id=list_id).first()
        if not shopping_list or not item:
            response = jsonify({
                'error_msg': "Requested shoppinglist item was not found"
            })
            response.status_code = 404
            return response

        if request.method == 'PUT':
            name = str(request.data.get('name', '')).lower().strip()

            error_message = validate_item_name(name, list_id)
            if error_message:
                return error_message

            item.name = name
            item.save()

            response = jsonify({
                'id': item.id,
                'name': item.name
            })
            response.status_code = 200

        elif request.method == 'DELETE':
            item.delete()
            response = jsonify({
                "message": "item {} has been deleted "
                           "successfully".format(item_id)
            })
            response.status_code = 200

        else:
            # retrieve the list with the id provided
            list_details = {
                'id': item.id,
                'name': item.name
            }

            response = jsonify(list_details)
            response.status_code = 200

        return response

    return flask_api


def validate_title(title):
    user_id = user_logged_in.id

    response = None
    if not title:
        response = jsonify(
            {
                'error_msg': "shoppinglist title must be provided"
            }
        )
        response.status_code = 400

    # check if similar shoppinglist owned by same user exists
    elif Shoppinglists.query.filter_by(title=title,
                                       user_id=user_id).first():
        response = jsonify(
            {
                'error_msg': "`{}` already exists".format(title)
            }
        )
        response.status_code = 409

    return response


def validate_item_name(name, list_id):
    response = None
    if not name:
        response = jsonify(
            {
                'error_msg': "Item name must be provided"
            }
        )
        response.status_code = 400

    elif ShoppingListItems.query.filter_by(
            name=name, shoppinglist_id=list_id).first():
        response = jsonify(
            {
                'error_msg': "Item `{}` already exists".format(name)
            }
        )
        response.status_code = 409

    return response


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


def verify_auth_token(token):
    s = Serializer(secret_key)

    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token

    user = User.query.get(data['id'])
    return user
