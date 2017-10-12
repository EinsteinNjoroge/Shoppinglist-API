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
        self.assertTrue('security_question' in [attr for attr in dir(self.user)])
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

    def test_api_reset_password(self):
        # Reset password without username
        reset_password_resource = self.client().get(
            '/user/reset_password/'
        )

        self.assertEqual(reset_password_resource.status_code, 400)
        self.assertIn('user is not specified in path',
                      str(reset_password_resource.data))

        # reset password for unregistered user
        reset_password_resource = self.client().get(
            '/user/reset_password/?user=ashgcvajac'
        )

        self.assertEqual(reset_password_resource.status_code, 404)
        self.assertIn('no registered user', str(reset_password_resource.data))

        # reset password for registered user
        self.get_authorization_header()
        reset_password_resource = self.client().get(
            '/user/reset_password/?user=user20nm'
        )

        self.assertEqual(reset_password_resource.status_code, 200)
        self.assertIn('myself?', str(reset_password_resource.data))

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

        # reset password with no password
        user_data = {
            'password': 'test_pword3'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('provide a valid answer',
                      str(change_password_resource.data))

        # reset password with no password
        user_data = {
            'password': 'wrong_answer'
        }

        change_password_resource = self.client().post(
            '/user/reset_password/?user=user20nm', data=user_data
        )
        self.assertEqual(change_password_resource.status_code, 400)
        self.assertIn('provide a valid answer',
                      str(change_password_resource.data))

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

    def test_api_create_duplicate_username(self):
        # create a user
        user_data1 = {
            'username': 'user100',
            'password': 'test_password',
            'security_question': 'AM i?',
            'answer': 'answer'
        }
        self.client().post('/user/register/', data=user_data1)

        # create another user with similar credentials
        create_user_resource = self.client().post(
            '/user/register/', data=user_data1
        )

        self.assertEqual(create_user_resource.status_code, 409)
        self.assertIn('username `{}` is already registered'.format('user100'),
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

    def test_crud_methods_of_shoppinglists(self):
        headers = self.get_authorization_header()

        # create a shoppinglists
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'back to school'},
            headers=headers
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        # test if API can create shoppinglists
        self.assertEqual(create_shoppinglist_resource.status_code, 201)
        self.assertIn('back to school', str(create_shoppinglist_resource.data))

        # test if API can retrieve created shoppinglists
        get_shoppinglist_resource = self.client().get(
            '/shoppinglist/',
            headers=headers
        )
        self.assertEqual(get_shoppinglist_resource.status_code, 200)
        self.assertIn('back to school', str(get_shoppinglist_resource.data))
        self.assertIn('created_on', str(get_shoppinglist_resource.data))
        self.assertIn('modified_on', str(get_shoppinglist_resource.data))

        # test API can update shoppinglist
        response = self.client().put(
            '/shoppinglist/{}'.format(shoppinglist_id),
            data={'title': "weekend party"},
            headers=headers
        )
        self.assertEqual(response.status_code, 200)

        # assert shoppinglist was updated successfully
        shoppinglist = self.client().get(
            '/shoppinglist/{}'.format(shoppinglist_id),
            headers=headers
        )
        self.assertIn('weekend party', str(shoppinglist.data))
        # get current timestamp
        epoch_time = time.time()
        timestamp = datetime.datetime.fromtimestamp(epoch_time).strftime(
            '%Y-%m-%d %H:%M')
        self.assertIn(timestamp, str(shoppinglist.data))

        # test API can delete shoppinglist
        # delete shoppinglist
        response = self.client().delete(
            '/shoppinglist/{}'.format(shoppinglist_id),
            headers=headers
        )
        self.assertEqual(response.status_code, 200)

        # assert shoppinglist was deleted successfully
        shoppinglist = self.client().get(
            '/shoppinglist/{}'.format(shoppinglist_id),
            headers=headers
        )
        self.assertEqual(shoppinglist.status_code, 404)

    def test_access_non_existent_shoppinglist(self):
        get_shoppinglist_resource = self.client().get(
            '/shoppinglist/123456789',
            headers=self.get_authorization_header()
        )
        self.assertEqual(get_shoppinglist_resource.status_code, 404)
        self.assertIn('Requested shoppinglist was not found',
                      str(get_shoppinglist_resource.data))

    def test_create_duplicate_shoppinglists(self):
        headers = self.get_authorization_header()

        # create a shoppinglists
        self.client().post(
            '/shoppinglist/',
            data={'title': 'Trip to canada'},
            headers=headers
        )

        # create a duplicate shoppinglists
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'trip to canada'},
            headers=headers
        )

        self.assertEqual(create_shoppinglist_resource.status_code, 409)
        self.assertIn('`trip to canada` already exists',
                      str(create_shoppinglist_resource.data))

    def test_search_for_non_existent_shoppinglists(self):
        # search shoppinglist
        search_shoppinglist_resource = self.client().get(
            '/shoppinglist/?q=shoppinglist one',
            headers=self.get_authorization_header()
        )

        self.assertIn('No shoppinglist matches the keyword `shoppinglist '
                      'one`',
                      str(search_shoppinglist_resource.data))
        self.assertEqual(search_shoppinglist_resource.status_code, 404)

    def test_search_shoppinglists(self):
        headers = self.get_authorization_header()

        # create a shoppinglists
        self.client().post(
            '/shoppinglist/',
            data={'title': 'trip to mombasa'},
            headers=headers
        )

        # search shoppinglist
        search_shoppinglist_resource = self.client().get(
            '/shoppinglist/?q=trip',
            headers=headers
        )

        self.assertEqual(search_shoppinglist_resource.status_code, 200)
        self.assertIn('trip to mombasa',
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

        self.assertEqual(get_paginated_shoppinglist_resource.status_code, 200)

        json_data = json.loads(
            get_paginated_shoppinglist_resource.data.decode(
                'utf-8').replace("'", "\"")
        )

        self.assertEqual(len(json_data), 100)

    def test_crud_methods_of_shoppinglist_items(self):
        headers = self.get_authorization_header()

        # create a shoppinglist
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'Trip to Dubai'},
            headers=headers
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        # test API can create shoppinglist item
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={'name': 'touring shoes', 'price': 10},
            headers=headers
        )
        self.assertEqual(create_item_resource.status_code, 201)
        self.assertIn('touring shoes', str(create_item_resource.data))

        # get id of item created
        json_item_resource = json.loads(
            create_item_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        item_id = json_item_resource['id']

        # test API can retrieve shoppinglist items
        get_item_resource = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            headers=headers
        )
        self.assertEqual(get_item_resource.status_code, 200)
        self.assertIn('touring shoes', str(get_item_resource.data))
        self.assertIn('price', str(get_item_resource.data))
        self.assertIn('quantity', str(get_item_resource.data))

        # test API can update shoppinglist item
        update_item_resource = self.client().put(
            '/items/{}'.format(item_id),
            data={
                'name': 'Swimming floaters',
                'price': '100',
                'quantity': '1'
            },
            headers=headers
        )
        self.assertEqual(update_item_resource.status_code, 200)

        # assert item was updated successfully
        items = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            headers=headers
        )
        self.assertIn('swimming floaters', str(items.data))

        # test API can delete shoppinglist item
        delete_item_resource = self.client().delete(
            '/items/{}'.format(item_id),
            headers=headers
        )
        self.assertEqual(delete_item_resource.status_code, 200)

        # asert item has been deleted successfully
        items = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            headers=headers
        )
        self.assertNotIn('swimming floaters', str(items.data))

    def test_shoppinglist_item_edge_cases(self):
        headers = self.get_authorization_header()

        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'Trip to Dubai'},
            headers=headers
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        # attempt to retrieve item that does not exist
        get_shoppinglist_resource = self.client().get(
            '/items/12345',
            headers=headers
        )
        self.assertEqual(get_shoppinglist_resource.status_code, 404)
        self.assertIn('Requested shoppinglist item was not found',
                      str(get_shoppinglist_resource.data))

        # create item with blank name
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={'price': '10'},
            headers=headers
        )
        self.assertEqual(create_item_resource.status_code, 400)
        self.assertIn('name must be provided', str(create_item_resource.data))

        # create item with no price
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={'name': 'item one'},
            headers=headers
        )
        self.assertEqual(create_item_resource.status_code, 400)
        self.assertIn('provide a valid item price',
                      str(create_item_resource.data))

        # Fetch items from list that doesn't exist
        create_item_resource = self.client().get(
            '/shoppinglist/{}/items/'.format(100000000000000000),
            headers=headers
        )
        self.assertEqual(create_item_resource.status_code, 404)
        self.assertIn('Requested shoppinglist was not found',
                      str(create_item_resource.data))

    def test_search_items(self):
        headers = self.get_authorization_header()

        # create a shoppinglist
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/',
            data={'title': 'Trip to Atlanta'},
            headers=headers
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        # search item that doesnt exist
        search_items_resource = self.client().get(
            '/shoppinglist/{}/items/?q=bread'.format(shoppinglist_id),
            headers=headers
        )

        self.assertEqual(search_items_resource.status_code, 404)
        self.assertIn('No item matches the keyword `bread`',
                      str(search_items_resource.data))

        # create an item
        self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={'name': 'touring shorts', 'price': '10'},
            headers=headers
        )

        # search items
        search_items_resource = self.client().get(
            '/shoppinglist/{}/items/?q=shorts'.format(shoppinglist_id),
            headers=headers
        )

        self.assertEqual(search_items_resource.status_code, 200)
        self.assertIn('touring shorts',
                      str(search_items_resource.data))

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

        self.app = None
        self.client = None
