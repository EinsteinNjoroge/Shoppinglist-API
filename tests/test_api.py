from base64 import b64encode
import time
import datetime
from flask import json
from unittest import TestCase
from app import create_app
from app.models import db
from app.models import User
from app.models import Shoppinglists
from app.models import ShoppingListItems
from app.models import generate_random_id
import app


class TestModels(TestCase):
    def setUp(self):
        self.user = User
        self.shoppinglist = Shoppinglists
        self.shoppinglist_items = ShoppingListItems

    def test_user_variables(self):
        """check if model User has the required class variables"""""
        self.assertTrue('id' in [attr for attr in dir(self.user)])
        self.assertTrue('username' in [attr for attr in dir(self.user)])
        self.assertTrue('firstname' in [attr for attr in dir(self.user)])
        self.assertTrue('lastname' in [attr for attr in dir(self.user)])
        self.assertTrue('password_hash' in [attr for attr in dir(self.user)])
        self.assertTrue('security_question' in
                        [attr for attr in dir(self.user)])
        self.assertTrue('answer' in [attr for attr in dir(self.user)])

    def test_shoppinglist_variables(self):
        """check if model ShoppingList has the required class variables"""
        self.assertTrue('id' in [attr for attr in dir(self.shoppinglist)])
        self.assertTrue('title' in [attr for attr in dir(self.shoppinglist)])
        self.assertTrue('user_id' in [attr for attr in dir(self.shoppinglist)])
        self.assertTrue('created_on' in [attr for attr in dir(
            self.shoppinglist)])
        self.assertTrue('modified_on' in [attr for attr in dir(
            self.shoppinglist)])

    def test_shoppinglist_items_variables(self):
        """check if model ShoppingListItems has the required class variables"""
        self.assertTrue('id' in
                        [attr for attr in dir(self.shoppinglist_items)])
        self.assertTrue('name' in
                        [attr for attr in dir(self.shoppinglist_items)])
        self.assertTrue('price' in
                        [attr for attr in dir(self.shoppinglist_items)])
        self.assertTrue('quantity' in
                        [attr for attr in dir(self.shoppinglist_items)])
        self.assertTrue('shoppinglist_id' in
                        [attr for attr in dir(self.shoppinglist_items)])

    def test_generate_random_int(self):
        """assert function `generate_random_id` returns an integer"""
        self.assertIsInstance(generate_random_id(), int)

    def tearDown(self):
        self.user = None
        self.shoppinglist = None
        self.shoppinglist_items = None


class TestAPI(TestCase):
    def setUp(self):
        self.app = create_app(config_mode="testing")

        with self.app.app_context():  # bind the app to the current context
            db.create_all()  # create all tables

        self.client = self.app.test_client

    # HELPER FUNCTIONS
    def get_authorization_header(self):
        # create a user and login to account created
        username = 'user20nm'
        pword = 'test_password'
        security_question = "Am I myself?"
        answer = 'yes'
        test_user = {'username': username, 'password': pword,
                     'answer': answer, 'security_question': security_question}
        self.client().post('/user/register/', data=test_user)

        header = {
            'Authorization': 'Basic ' + b64encode(
                bytes("{0}:{1}".format(username, pword), 'ascii')
            ).decode('ascii')
        }
        return header

    def create_shoppinglist_resource(self):
        headers = self.get_authorization_header()

        # create a shoppinglists
        shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'back to school'},
            headers=headers
        )
        return shoppinglist_resource

    def get_shoppinglist_resource(self):
        headers = self.get_authorization_header()
        self.create_shoppinglist_resource()
        shoppinglist_resource = self.client().get(
            '/shoppinglist/',
            headers=headers
        )
        return shoppinglist_resource

    def get_shoppinglist_id(self):
        create_shoppinglist_resource = self.create_shoppinglist_resource()
        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']
        return shoppinglist_id

    @staticmethod
    def get_current_timestamp():
        # get current timestamp
        epoch_time = time.time()
        timestamp = datetime.datetime.fromtimestamp(epoch_time).strftime(
            '%Y-%m-%d %H:%M')
        return timestamp

    def create_item_resource(self, shoppinglist_id=None):
        headers = self.get_authorization_header()
        if not shoppinglist_id:
            shoppinglist_id = self.get_shoppinglist_id()

        item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={'name': 'touring shoes', 'price': 10},
            headers=headers
        )
        return item_resource

    def get_item_id(self):
        create_item_resource = self.create_item_resource()

        # get id of item created
        json_item_resource = json.loads(
            create_item_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        item_id = json_item_resource['id']

        return item_id

    # END HELPER FUNCTIONS

    def test_api_index_page(self):
        index_page = self.client().get('/')

        self.assertEqual(index_page.status_code, 200)
        self.assertIn('WELCOME', str(index_page.data))

    def test_api_nonexistent_route(self):
        index_page = self.client().get('/saghs')

        self.assertEqual(index_page.status_code, 404)
        self.assertIn('not exist', str(index_page.data))

    def test_api_method_not_allowed(self):
        index_page = self.client().post('/')

        self.assertEqual(index_page.status_code, 405)
        self.assertIn('not allowed', str(index_page.data))

    def test_api_user_password_complexity(self):
        user_data = {
            'username': 'test_user200',
            'password': '123',
            'security_question': 'AM i?',
            'answer': 'answer'
        }
        create_user_resource = self.client().post(
            '/user/register/', data=user_data
        )

        self.assertEqual(create_user_resource.status_code, 409)
        self.assertIn('password must be at-least 6',
                      str(create_user_resource.data))

    def test_api_create_user_without_credentials(self):
        create_user_resource = self.client().post(
            '/user/register/', data=None
        )

        self.assertEqual(create_user_resource.status_code, 400)
        self.assertIn('provide a valid username and password',
                      str(create_user_resource.data))

    def test_api_create_user_without_security_question(self):
        user_data = {
            'username': 'test_user200',
            'password': '123'
        }
        create_user_resource = self.client().post(
            '/user/register/', data=user_data
        )

        self.assertEqual(create_user_resource.status_code, 400)
        self.assertIn('provide a valid security question',
                      str(create_user_resource.data))

    def test_api_create_user(self):
        user_data = {
            'username': 'test_user2',
            'password': 'test_password',
            'security_question': 'AM i?',
            'answer': 'answer'
        }
        create_user_resource = self.client().post(
            '/user/register/', data=user_data
        )

        self.assertEqual(create_user_resource.status_code, 201)
        self.assertIn('test_user', str(create_user_resource.data))
        self.assertIn('id', str(create_user_resource.data))

    def test_api_change_password_with_blank_new_password(self):
        headers = self.get_authorization_header()
        user_data = {'password': ''}
        change_password_resource = self.client().put(
            '/user/change_password/', data=user_data, headers=headers
        )

        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('provide a valid password',
                      str(change_password_resource.data))

    def test_api_change_password(self):
        headers = self.get_authorization_header()
        user_data = {'password': 'new_password'}
        change_password_resource = self.client().put(
            '/user/change_password/', data=user_data, headers=headers
        )

        self.assertEqual(change_password_resource.status_code, 200)
        self.assertIn('successfully', str(change_password_resource.data))

    def test_api_reset_password_with_no_user(self):
        # Reset password without username
        reset_password_resource = self.client().get(
            '/user/reset_password/'
        )

        self.assertEqual(reset_password_resource.status_code, 400)
        self.assertIn('user is not specified in path',
                      str(reset_password_resource.data))

    def test_api_reset_password_unregistered_user(self):
        # reset password for unregistered user
        reset_password_resource = self.client().get(
            '/user/reset_password/?user=ashgcvajac'
        )

        self.assertEqual(reset_password_resource.status_code, 404)
        self.assertIn('no registered user', str(reset_password_resource.data))

    def test_api_reset_password_get_security_question(self):
        # reset password for registered user
        self.get_authorization_header()
        reset_password_resource = self.client().get(
            '/user/reset_password/?user=user20nm'
        )

        self.assertEqual(reset_password_resource.status_code, 200)
        self.assertIn('myself?', str(reset_password_resource.data))

    def test_api_reset_password_wrong_answer(self):
        self.get_authorization_header()
        # reset password with wrong answer
        user_data = {
            'password': 'test_password3',
            'answer': 'wrong_answer'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('answer is incorrect',
                      str(change_password_resource.data))

    def test_api_reset_password_no_password(self):
        self.get_authorization_header()
        # reset password with no password
        user_data = {
            'answer': 'wrong_answer'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('Please provide a valid password',
                      str(change_password_resource.data))

    def test_api_reset_password_no_answer(self):
        self.get_authorization_header()
        # reset password with no answer
        user_data = {
            'password': 'test_pword3'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('provide a valid answer',
                      str(change_password_resource.data))

    def test_api_reset_password_successful(self):
        self.get_authorization_header()
        # reset password with correct credentials
        user_data = {
            'password': 'est_password454',
            'answer': 'yes'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 200)
        self.assertIn('successfully',
                      str(change_password_resource.data))

    def test_api_logout(self):
        user_logout = self.client().get('/user/logout/')

        self.assertEqual(user_logout.status_code, 200)
        self.assertIn('User logged out', str(user_logout.data))

    def test_invalid_verify_auth_token(self):
        token = app.verify_auth_token("gdfchvjkbl")
        self.assertEqual(None, token)

    def test_api_create_duplicate_username(self):
        # create a user
        self.get_authorization_header()

        # create another user with similar credentials
        user_data1 = {
            'username': 'user20nm',
            'password': 'test_password',
            'security_question': 'AM i?',
            'answer': 'answer'
        }
        create_user_resource = self.client().post(
            '/user/register/', data=user_data1
        )

        self.assertEqual(create_user_resource.status_code, 409)
        self.assertIn('is already registered'.format('user100'),
                      str(create_user_resource.data))

    def test_api_authenticate_user_without_credentials(self):
        create_user_resource = self.client().post(
            '/user/login/', data=None
        )

        self.assertEqual(create_user_resource.status_code, 400)
        self.assertIn('provide a valid username and password',
                      str(create_user_resource.data))

    def test_api_authenticate_user(self):
        user_data = {
            'username': 'test_user10',
            'password': 'test_password',
            'security_question': 'AM i?',
            'answer': 'answer'
        }

        # create a user
        self.client().post('/user/register/', data=user_data)

        # Login to account created
        authenticate_user_resource = self.client().post(
            '/user/login/', data=user_data
        )

        self.assertEqual(authenticate_user_resource.status_code, 200)
        self.assertIn('token', str(authenticate_user_resource.data))

    def test_api_authenticate_user_with_wrong_credentials(self):
        user_data2 = {
            'username': 'trcyujkhbguvy5h',
            'password': 'test_password'
        }

        # Login to account created
        authenticate_user_resource = self.client().post(
            '/user/login/', data=user_data2
        )

        self.assertEqual(authenticate_user_resource.status_code, 401)
        self.assertIn('Wrong', str(authenticate_user_resource.data))

    def test_create_shoppinglists_with_blank_title(self):
        # create a shoppinglists
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data=None,
            headers=self.get_authorization_header()
        )

        self.assertEqual(create_shoppinglist_resource.status_code, 400)
        self.assertIn('title must be provided',
                      str(create_shoppinglist_resource.data))

    def test_create_shoppinglists(self):
        create_shoppinglist_resource = self.create_shoppinglist_resource()

        # test if API can create shoppinglists
        self.assertEqual(create_shoppinglist_resource.status_code, 201)
        self.assertIn('back to school', str(create_shoppinglist_resource.data))

    def test_get_shoppinglists(self):
        # test if API can retrieve created shoppinglists
        get_shoppinglist_resource = self.get_shoppinglist_resource()
        self.assertEqual(get_shoppinglist_resource.status_code, 200)
        self.assertIn('back to school', str(get_shoppinglist_resource.data))
        self.assertIn('created_on', str(get_shoppinglist_resource.data))
        self.assertIn('modified_on', str(get_shoppinglist_resource.data))

    def test_update_shoppinglists_without_title(self):
        shoppinglist_id = self.get_shoppinglist_id()

        # test API can update shoppinglist
        response = self.client().put(
            '/shoppinglist/{}'.format(shoppinglist_id),
            data={'title': ""},
            headers=self.get_authorization_header()
        )
        # assert shoppinglist was updated successfully
        self.assertEqual(response.status_code, 400)
        self.assertIn('title must be provided', str(response.data))

    def test_retrieve_shoppinglists(self):
        shoppinglist_id = self.get_shoppinglist_id()

        # test API can update shoppinglist
        response = self.client().get(
            '/shoppinglist/{}'.format(shoppinglist_id),
            headers=self.get_authorization_header()
        )
        # assert shoppinglist was updated successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', str(response.data))
        self.assertIn(self.get_current_timestamp(), str(response.data))

    def test_update_shoppinglists(self):
        shoppinglist_id = self.get_shoppinglist_id()

        # test API can update shoppinglist
        response = self.client().put(
            '/shoppinglist/{}'.format(shoppinglist_id),
            data={'title': "weekend party"},
            headers=self.get_authorization_header()
        )
        # assert shoppinglist was updated successfully
        self.assertEqual(response.status_code, 200)
        self.assertIn('weekend party', str(response.data))
        self.assertIn(self.get_current_timestamp(), str(response.data))

    def test_delete_shoppinglists(self):
        # test API can delete shoppinglist
        # delete shoppinglist
        response = self.client().delete(
            '/shoppinglist/{}'.format(self.get_shoppinglist_id()),
            headers=self.get_authorization_header()
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully", str(response.data))

    def test_access_non_existent_shoppinglist(self):
        get_shoppinglist_resource = self.client().get(
            '/shoppinglist/123456789',
            headers=self.get_authorization_header()
        )
        self.assertEqual(get_shoppinglist_resource.status_code, 404)
        self.assertIn('Requested shoppinglist was not found',
                      str(get_shoppinglist_resource.data))

    def test_create_duplicate_shoppinglists(self):
        # create a shoppinglists
        self.create_shoppinglist_resource()

        # create a duplicate shoppinglists
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'back to school'},
            headers=self.get_authorization_header()
        )

        self.assertEqual(create_shoppinglist_resource.status_code, 409)
        self.assertIn('already exists', str(create_shoppinglist_resource.data))

    def test_search_for_non_existent_shoppinglists(self):
        # search shoppinglist
        search_shoppinglist_resource = self.client().get(
            '/shoppinglist/?q=shoppinglist one',
            headers=self.get_authorization_header()
        )

        self.assertIn('No shoppinglist matches the keyword',
                      str(search_shoppinglist_resource.data))
        self.assertEqual(search_shoppinglist_resource.status_code, 404)

    def test_search_shoppinglists(self):
        headers = self.get_authorization_header()

        # create a shoppinglists
        self.create_shoppinglist_resource()

        # search shoppinglist
        search_shoppinglist_resource = self.client().get(
            '/shoppinglist/?q=back',
            headers=headers
        )

        self.assertEqual(search_shoppinglist_resource.status_code, 200)
        self.assertIn('back to school',
                      str(search_shoppinglist_resource.data))

    def test_shoppinglists_pagination(self):
        headers = self.get_authorization_header()

        # create 1000 shoppinglists
        i = 0
        while i < 1000:
            data = {'title': 'trip {} to Dubai'.format(i)}
            self.client().post('/shoppinglist/', data=data, headers=headers)
            i += 1

        # get shoppinglists with pagination
        get_paginated_shoppinglist_resource = self.client().get(
            '/shoppinglist/?limit=100',
            headers=headers
        )

        # covert response array to json
        json_data = json.loads(
            get_paginated_shoppinglist_resource.data.decode(
                'utf-8').replace("'", "\"")
        )

        self.assertEqual(get_paginated_shoppinglist_resource.status_code, 200)
        self.assertEqual(len(json_data), 100)

    def test_create_shoppinglist_item(self):
        create_item_resource = self.create_item_resource()

        # test API can create shoppinglist item
        self.assertEqual(create_item_resource.status_code, 201)
        self.assertIn('touring shoes', str(create_item_resource.data))

    def test_retrieve_shoppinglist_items(self):
        # test API can retrieve shoppinglist items
        get_item_resource = self.client().get(
            '/items/{}'.format(self.get_item_id()),
            headers=self.get_authorization_header()
        )
        self.assertEqual(get_item_resource.status_code, 200)
        self.assertIn('touring shoes', str(get_item_resource.data))
        self.assertIn('price', str(get_item_resource.data))
        self.assertIn('quantity', str(get_item_resource.data))

    def test_update_item(self):
        # test API can update shoppinglist item
        update_item_resource = self.client().put(
            '/items/{}'.format(self.get_item_id()),
            data={
                'name': 'Swimming floaters',
                'price': '100',
                'quantity': '1'
            },
            headers=self.get_authorization_header()
        )
        self.assertEqual(update_item_resource.status_code, 200)
        self.assertIn('swimming floaters', str(update_item_resource.data))

    def test_delete_item(self):
        # test API can delete shoppinglist item
        delete_item_resource = self.client().delete(
            '/items/{}'.format(self.get_item_id()),
            headers=self.get_authorization_header()
        )
        self.assertEqual(delete_item_resource.status_code, 200)
        self.assertIn('successfully', str(delete_item_resource.data))

    def test_get_item_that_doesnt_exist(self):
        headers = self.get_authorization_header()

        # attempt to retrieve item that does not exist
        get_shoppinglist_resource = self.client().get(
            '/items/12345',
            headers=headers
        )
        self.assertEqual(get_shoppinglist_resource.status_code, 404)
        self.assertIn('Requested shoppinglist item was not found',
                      str(get_shoppinglist_resource.data))

    def test_create_blank_item(self):
        # create item with blank name
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(self.get_shoppinglist_id()),
            data={'price': '10'},
            headers=self.get_authorization_header()
        )
        self.assertEqual(create_item_resource.status_code, 400)
        self.assertIn('name must be provided', str(create_item_resource.data))

    def test_create_item_with_no_price(self):
        # create item with no price
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(self.get_shoppinglist_id()),
            data={'name': 'item one'},
            headers=self.get_authorization_header()
        )
        self.assertEqual(create_item_resource.status_code, 400)
        self.assertIn('provide a valid item price',
                      str(create_item_resource.data))

    def test_create_item_with_invalid_quantity(self):
        # create item with invalid quantity
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(self.get_shoppinglist_id()),
            data={'name': 'item one',
                  'price': 30,
                  'quantity': 'ff'},
            headers=self.get_authorization_header()
        )
        self.assertEqual(create_item_resource.status_code, 400)
        self.assertIn('provide a valid quantity',
                      str(create_item_resource.data))

    def test_retrieve_items_from_none_existent_list(self):
        # Fetch items from list that doesn't exist
        create_item_resource = self.client().get(
            '/shoppinglist/{}/items/'.format(100000000000000000),
            headers=self.get_authorization_header()
        )
        self.assertEqual(create_item_resource.status_code, 404)
        self.assertIn('Requested shoppinglist was not found',
                      str(create_item_resource.data))

    def test_search_items_that_doesnt_exist(self):

        # search item that doesnt exist
        search_items_resource = self.client().get(
            '/shoppinglist/{}/items/?q=bread'.format(
                self.get_shoppinglist_id()),
            headers=self.get_authorization_header()
        )

        self.assertEqual(search_items_resource.status_code, 404)
        self.assertIn('No item matches the keyword `bread`',
                      str(search_items_resource.data))

    def test_search_item(self):
        shoppinglist_id = self.get_shoppinglist_id()
        self.create_item_resource(shoppinglist_id)

        # search items
        search_items_resource = self.client().get(
            '/shoppinglist/{}/items/?q=tour'.format(
                shoppinglist_id),
            headers=self.get_authorization_header()
        )

        self.assertEqual(search_items_resource.status_code, 200)
        self.assertIn('tour', str(search_items_resource.data))

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

        self.app = None
        self.client = None
