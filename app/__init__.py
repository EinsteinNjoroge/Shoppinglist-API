import hashlib
import os
import time
import datetime
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


def create_app(config_mode):
    flask_api = FlaskAPI(__name__, instance_relative_config=True)
    flask_api.config.from_object(configurations[config_mode])
    flask_api.config.from_pyfile('config.py')
    flask_api.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_api.secret_key = secret_key
    db.init_app(flask_api)
    auth = HTTPBasicAuth()

    @flask_api.route('/', methods=['GET'])
    def index():

        data = {
            "message": "WELCOME TO THE SHOPPINGLIST API. KEEP TRACK OF YOUR "
                       "SHOPPING CARTS AND ITEMS."
        }
        return make_response(data, status_code=200)

    @flask_api.errorhandler(404)
    def route_not_found(e):
        data = {
            "error_msg": "Route does not exist. Please check the path you "
                         "provided and try again"
        }
        return make_response(data, status_code=405)

    @flask_api.errorhandler(405)
    def method_not_allowed(e):
        data = {
            "error_msg": "This method is not allowed on this path"
        }
        return make_response(data, status_code=405)

    @flask_api.route('/user/register/', methods=['POST'])
    def create_user():
        """Creates a user account

            :arg:
                pword (string): Users password
                username (string): user's unique name

            :return
                response (json):
        """
        # Create a user account with the credentials provided
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', '')).lower().strip()
        answer = str(request.data.get('answer', '')).lower().strip()
        security_question = str(request.data.get('security_question',
                                                 '')).lower().strip()

        if not username or not pword:
            data = {
                "error_msg": "Please provide a valid username and password"
            }
            return make_response(data, status_code=400)

        if not answer or not security_question:
            data = {
                "error_msg": "Please provide a valid security question and "
                             "answer"
            }
            return make_response(data, status_code=400)

        if len(pword) < 6:
            data = {
                "error_msg": "password must be at-least 6 characters long"
            }
            return make_response(data, status_code=409)

        # Check username is already registered
        if User.query.filter_by(username=username).first():
            data = {
                "error_msg": "username `{}` is already registered. Please "
                             "provide a unique username".format(username)
            }
            return make_response(data, status_code=409)

        # Create a user
        password_hash = sha1_hash(pword)
        new_user = User(username=username, password_hash=password_hash,
                        answer=answer, security_question=security_question)
        new_user.save()

        data = {
            "message": "user `{}` has been created".format(username),
            "id": new_user.id
        }
        return make_response(data, status_code=201)

    @flask_api.route('/user/login/', methods=['POST'])
    def authenticate_user():
        pword = str(request.data.get('password', ''))
        username = str(request.data.get('username', ''))

        if not username or not pword:
            data = {
                "error_msg": "Please provide a valid username and password"
            }
            return make_response(data, status_code=400)

        if verify_password(username, pword):
            token = generate_auth_token()
            data = {
                "token": token.decode('ascii')
            }
            return make_response(data, status_code=200)

        data = {
            "message": "Wrong credentials combination"
        }
        return make_response(data, 401)

    @auth.verify_password
    def verify_password(username, pword):
        """Check if credentials or token provided is authentic

                :arg:
                    username (string): User's unique name or
                        authentication token
                    pword (string): User's password

                :return
                    (boolen): True if user has been authorised, otherwise
                    returns False
            """
        # Attempt to authenticate using token
        user = verify_auth_token(username)

        if not user:
            # attempt authentication using password
            password_hash = sha1_hash(pword)
            user = User.query.filter_by(username=username,
                                        password_hash=password_hash).first()
        if user:
            # Credentials are authentic
            global user_logged_in
            user_logged_in = user
            return True

        return False

    @flask_api.route('/user/logout/', methods=['GET'])
    def logout_user():
        global user_logged_in
        user_logged_in = None
        data = {
            "message": "User logged out"
        }
        return make_response(data, 200)

    @flask_api.route('/user/change_password/', methods=['PUT'])
    @auth.login_required
    def change_password():

        pword = str(request.data.get('password', ''))

        if not pword:
            data = {
                "error_msg": "Please provide a valid password"
            }
            return make_response(data, status_code=400)

        user_logged_in.password_hash = sha1_hash(pword)
        user_logged_in.save()
        data = {
            'message': "Password has been changed successfully"
        }
        return make_response(data, 200)

    @flask_api.route('/user/reset_password/', methods=['GET', 'POST'])
    def reset_password():

        args = request.args
        if not args or 'user' not in args:
            data = {
                "error_msg": "user is not specified in path"
            }
            return make_response(data, status_code=400)

        username = str(args['user'])
        user = User.query.filter_by(username=username).first()

        # Get security question
        if request.method == 'GET':

            if not user:
                data = {
                    "error_msg": "There is no registered user with the "
                                 "username `{}`".format(username)
                }
                return make_response(data, status_code=404)

            data = {
                "security_question": user.security_question
            }
            return make_response(data, status_code=200)

        # METHOD POST
        # reset password
        pword = str(request.data.get('password', ''))
        answer = str(request.data.get('answer', ''))

        if not pword or len(pword) < 6:
            data = {
                "error_msg": "Please provide a valid password (At-least 6 "
                             "characters)"
            }
            return make_response(data, status_code=400)

        if not answer:
            data = {
                "error_msg": "Please provide a valid answer for the"
                             " security question"
            }
            return make_response(data, status_code=400)

        if user.answer.lower() != answer.lower():
            data = {
                "error_msg": "Your security question answer is incorrect."
            }
            return make_response(data, status_code=400)

        user.password_hash = sha1_hash(pword)
        user.save()
        data = {
            'message': "Password has been reset successfully"
        }
        return make_response(data, 200)

    @flask_api.route('/shoppinglist/', methods=['POST', 'GET'])
    @auth.login_required
    def shoppinglists():

        user_id = user_logged_in.id

        if request.method == 'POST':

            # Create a shoppinglist with title provided
            title = str(request.data.get('title', '')).lower().strip()

            # check if title is valid
            error_message = validate_title(title)
            if error_message:
                return error_message

            # create shoppinglist
            shopping_list = Shoppinglists(title=title, user_id=user_id)
            shopping_list.save()
            data = {
                'id': shopping_list.id,
                'title': shopping_list.title
            }
            return make_response(data, status_code=201)

        # METHOD GET

        shopping_lists = None
        limit = None

        # check if GET parameters has been parsed with the path
        args = request.args
        if args:

            if 'limit' in args:
                # limit number of results returned
                limit = int(args['limit'])

            if 'q' in args:
                # search for shoppinglists that contain keyword provided
                keyword = str(args['q']).lower()

                if limit:
                    # search with pagination
                    shopping_lists = Shoppinglists.query.filter(
                        Shoppinglists.title.like("%{}%".format(keyword)),
                        Shoppinglists.user_id == user_id
                    ).limit(limit).all()

                else:
                    # search without pagination
                    shopping_lists = Shoppinglists.query.filter(
                        Shoppinglists.title.like("%{}%".format(keyword)),
                        Shoppinglists.user_id == user_id
                    ).all()

                if len(shopping_lists) < 1:
                    data = {
                        'error_msg': "No shoppinglist matches "
                                     "the keyword `{}`.".format(keyword)
                    }
                    return make_response(data, 404)

        if not shopping_lists:
            if limit:
                # Limit number of shoppinglists returned
                shopping_lists = Shoppinglists.query.filter_by(
                    user_id=user_id).limit(limit)
            else:
                # Retrieve all shoppinglists
                shopping_lists = Shoppinglists.query.filter_by(
                    user_id=user_id).all()

        data = []
        for shopping_list in shopping_lists:
            list_details = {
                'id': shopping_list.id,
                'title': shopping_list.title,
                'created_on': shopping_list.created_on,
                'modified_on': shopping_list.modified_on
            }
            data.append(list_details)
        return make_response(data, status_code=200)

    @flask_api.route('/shoppinglist/<int:list_id>',
                     methods=['PUT', 'GET', 'DELETE'])
    @auth.login_required
    def shoppinglist(list_id):
        user_id = user_logged_in.id

        # check if shoppinglist with id <list_id> exists
        shopping_list = Shoppinglists.query.filter_by(id=list_id,
                                                      user_id=user_id).first()
        if not shopping_list:
            data = {
                'error_msg': "Requested shoppinglist was not found"
            }
            return make_response(data, status_code=404)

        if request.method == 'PUT':
            title = str(request.data.get('title', '')).lower().strip()

            error_message = validate_title(title)
            if error_message:
                return error_message

            # get current timestamp
            epoch_time = time.time()
            timestamp = datetime.datetime.fromtimestamp(epoch_time).strftime(
                '%Y-%m-%d %H:%M:%S')

            shopping_list.title = title
            shopping_list.modified_on = timestamp
            shopping_list.save()

            data = {
                'id': shopping_list.id,
                'title': shopping_list.title,
                'modified_on': shopping_list.modified_on
            }
            return make_response(data, 200)

        if request.method == 'DELETE':
            shopping_list.delete()
            data = {
                "message": "shoppinglist {} has been deleted "
                           "successfully".format(list_id)
            }
            return make_response(data, status_code=200)

        # retrieve the list with the id provided
        list_details = {
            'id': shopping_list.id,
            'title': shopping_list.title,
            'modified_on': shopping_list.modified_on,
            'created_on': shopping_list.created_on
        }
        return make_response(list_details, status_code=200)

    @flask_api.route('/shoppinglist/<int:list_id>/items/',
                     methods=['POST', 'GET'])
    @auth.login_required
    def shoppinglist_items(list_id):

        user_id = user_logged_in.id
        shopping_list = Shoppinglists.query.filter_by(id=list_id,
                                                      user_id=user_id).first()
        if not shopping_list:
            data = {'error_msg': "Requested shoppinglist was not found"}
            return make_response(data, status_code=404)

        if request.method == 'POST':
            # Create shoppinglist item with the name provided
            name = str(request.data.get('name', '')).lower().strip()
            price = str(request.data.get('price', ''))
            quantity = str(request.data.get('quantity', '1'))

            error_message = validate_item_name(name, list_id)

            if not error_message:
                error_message = validate_item_price_and_quantity(
                    price, quantity)

            if error_message:
                return error_message

            item = ShoppingListItems(name=name, shoppinglist_id=list_id,
                                     price=price, quantity=quantity)
            item.save()
            data = {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity
            }
            return make_response(data, status_code=201)

        # METHOD GET

        items = None
        limit = None

        # check if a search keyword has been provided
        args = request.args
        if args:

            if 'limit' in args:
                # limit number of results returned
                limit = int(args['limit'])

            if 'q' in args:
                # search for item that contain keyword provided
                keyword = str(args['q']).lower()

                if limit:
                    # limit number of results returned
                    items = ShoppingListItems.query.filter(
                        ShoppingListItems.name.like(
                            "%{}%".format(keyword)),
                        ShoppingListItems.shoppinglist_id == list_id
                    ).limit(limit).all()

                else:
                    # get all results that match keyword
                    items = ShoppingListItems.query.filter(
                        ShoppingListItems.name.like(
                            "%{}%".format(keyword)
                        ), ShoppingListItems.shoppinglist_id == list_id
                    ).all()

                # if no items contains keyword
                if len(items) < 1:
                    data = {'error_msg': "No item matches the keyword "
                                         "`{}`.".format(keyword)}
                    return make_response(data, status_code=404)

        if not items:

            if limit:
                # limit number or results to be returned
                items = ShoppingListItems.query.filter_by(
                    shoppinglist_id=list_id).limit(limit).all()
            else:
                #  return all results
                items = ShoppingListItems.query.filter_by(
                    shoppinglist_id=list_id)

        data = []
        for item in items:
            list_details = {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity
            }
            data.append(list_details)
        return make_response(data, status_code=200)

    @flask_api.route('/items/<int:item_id>',
                     methods=['PUT', 'GET', 'DELETE'])
    @auth.login_required
    def shoppinglist_item(item_id):

        user_id = user_logged_in.id

        item = ShoppingListItems.query.filter_by(
            id=item_id).first()

        if not item:
            data = {'error_msg': "Requested shoppinglist item was not found"}
            return make_response(data=data, status_code=404)

        shoppinglist_id = item.shoppinglist_id
        shopping_list = Shoppinglists.query.filter_by(id=shoppinglist_id,
                                                      user_id=user_id).first()

        if not shopping_list:
            data = {'error_msg': "Requested shoppinglist item was not found"}
            return make_response(data=data, status_code=404)

        if request.method == 'PUT':
            name = str(request.data.get('name', '')).lower().strip()
            price = str(request.data.get('price', ''))
            quantity = str(request.data.get('quantity', ''))

            # check if item name is valid
            error_message = validate_item_name(name, shoppinglist_id)

            if not error_message:
                error_message = validate_item_price_and_quantity(
                    price, quantity)

            if error_message:
                return error_message

            item.name = name
            item.price = price
            item.quantity = quantity
            item.save()

            data = {'id': item.id, 'name': item.name}
            return make_response(data=data, status_code=200)

        if request.method == 'DELETE':
            item.delete()
            data = {"message": "item {} has been deleted "
                               "successfully".format(item_id)}
            return make_response(data=data, status_code=200)

        # retrieve the list with the id provided
        data = {
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'quantity': item.quantity
        }
        return make_response(data, status_code=200)

    return flask_api


def make_response(data, status_code):
    """Convert dictionary provided to a json array and adds a status code to
    the dictionary

        :arg:
            data (dict): Dictionary to be converted to json array
            status_code (int):

        :return
            response (json):
    """
    response = jsonify(data)
    response.status_code = status_code
    return response


def validate_title(title):
    """Validates that a title has the at-least one character and that no
        other shoppinglist - belonging to the current user - has a similar
        title

        :arg:
            title (string): The title of shoppinglist to be created

        :return
            response (json): Error message generated if any, otherwise
            returns None
    """
    user_id = user_logged_in.id

    if not title:
        data = {
            'error_msg': "shoppinglist title must be provided"
        }
        return make_response(data, status_code=400)

    # check if similar shoppinglist owned by same user exists
    if Shoppinglists.query.filter_by(title=title,
                                     user_id=user_id).first():
        data = {
            'error_msg': "`{}` already exists".format(title)
        }
        return make_response(data, status_code=409)


def validate_item_name(name, list_id):
    """Validates that a name has the at-least one character and that no
    other item - belonging to the current user - has a similar name

        :arg:
            name (string): The name of item to be created
            list_id (int): ID of the shoppinglist where item will be created

        :return
            response (json): Error message generated if any, otherwise
            returns None
    """

    if not name:
        data = {
            'error_msg': "Item name must be provided"
        }
        return make_response(data, status_code=400)

    if ShoppingListItems.query.filter_by(
            name=name, shoppinglist_id=list_id).first():
        data = {
            'error_msg': "Item `{}` already exists".format(name)
        }
        return make_response(data, status_code=409)


def validate_item_price_and_quantity(price, quantity):
    """Validates that a name has the at-least one character and that no
    other item - belonging to the current user - has a similar name

        :arg:
            name (string): The name of item to be created
            list_id (int): ID of the shoppinglist where item will be created

        :return
            response (json): Error message generated if any, otherwise
            returns None
    """
    if not price.isdigit():
        data = {
            'error_msg': "Please provide a valid item price"
        }
        return make_response(data, status_code=400)

    if not quantity.isdigit():
        data = {
            'error_msg': "Please provide a valid quantity"
        }
        return make_response(data, status_code=400)


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


def generate_auth_token():
    """Creates a user authentication token using the user's ID

        :arg:
            user (object): User to be authenticated

        :return
            (byte): Authentication token
    """
    s = Serializer(secret_key, expires_in=600)
    return s.dumps({'id': user_logged_in.id})


def verify_auth_token(token):
    """Checks an authentication token to validate that it has a valid user's ID
    and is not expired

        :arg:
            token (string): Authentication token provided

        :return
            (boolean): True if token is valid otherwise returns False
    """
    serializer = Serializer(secret_key)

    try:
        data = serializer.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token

    user = User.query.get(data['id'])
    return user
