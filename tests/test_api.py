from flask import json
from unittest import TestCase
from app import launch_app
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
        self.assertTrue('password_hash' in [attr for attr in dir(self.user)])
        self.assertTrue('firstname' in [attr for attr in dir(self.user)])
        self.assertTrue('lastname' in [attr for attr in dir(self.user)])

    def test_shoppinglist_variables(self):
        """check if model ShoppingList has the required class variables"""
        self.assertTrue('id' in [attr for attr in dir(self.shoppinglist)])
        self.assertTrue('title' in [attr for attr in dir(self.shoppinglist)])
        self.assertTrue('user_id' in [attr for attr in dir(self.shoppinglist)])

    def test_shoppinglist_items_variables(self):
        """check if model ShoppingListItems has the required class variables"""
        self.assertTrue('id' in
                        [attr for attr in dir(self.shoppinglist_items)])
        self.assertTrue('name' in
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
        self.app = launch_app(config_mode="testing")

        with self.app.app_context():  # bind the app to the current context
            db.create_all()  # create all tables

        self.client = self.app.test_client

    def test_api_can_create_user(self):
        create_user_resource = self.client().post(
            '/user/register/', data={
                'username': 'test_user',
                'password': 'test_password'
            }
        )

        self.assertEqual(create_user_resource.status_code, 201)
        self.assertIn('test_user', str(create_user_resource.data))
        self.assertIn('id', str(create_user_resource.data))

#     def test_api_can_authenticate_user(self):
#         username = 'test_user'
#         pword = 'test_password'
#         data = {
#             'username': username,
#             'password': pword
#         }
#
#         # create a user
#         self.client().post('/user/register/', data=data)
#
#         authenticate_user_resource = self.client().post(
#             '/user/login/', data=data
#         )
#
#         self.assertEqual(authenticate_user_resource.status_code, 201)
#         self.assertIn('login successful', str(authenticate_user_resource.data))

    def test_shoppinglists(self):
        # create a user and get user's id
        test_user = {'username': 'test_user2', 'password': 'test_password'}
        user_resource = json.loads(
            self.client().post('/user/register/', data=test_user).data
                .decode('utf-8').replace("'", "\"")
        )
        user_id = user_resource['id']

        # create a shoppinglists
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/', data={
                'title': 'Back to school',
                'user_id': user_id
            }
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        """test if API can create shoppinglists"""
        self.assertEqual(create_shoppinglist_resource.status_code, 201)
        self.assertIn('Back to school', str(create_shoppinglist_resource.data))

        """test if API can retrieve created shoppinglists"""
        get_shoppinglist_resource = self.client().get('/shoppinglist/')
        self.assertEqual(get_shoppinglist_resource.status_code, 200)
        self.assertIn('Back to school', str(get_shoppinglist_resource.data))

        """test API can update shoppinglist"""
        # Update current shoppinglist
        response = self.client().put(
            '/shoppinglist/{}'.format(shoppinglist_id),
            data={'title': "Weekend party"}
        )
        self.assertEqual(response.status_code, 200)

        # assert shoppinglist was updated successfully
        shoppinglist = self.client().get(
            '/shoppinglist/{}'.format(shoppinglist_id)
        )
        self.assertIn('Weekend party', str(shoppinglist.data))

        """test API can delete shoppinglist"""
        # delete shoppinglist
        response = self.client().delete('/shoppinglist/{}'.format(
            shoppinglist_id))
        self.assertEqual(response.status_code, 200)

        # assert shoppinglist was deleted successfully
        shoppinglist = self.client().get(
            '/shoppinglist/{}'.format(shoppinglist_id)
        )
        self.assertEqual(shoppinglist.status_code, 404)

    def test_shoppinglists_items(self):
        # create a user and get user's id
        test_user = {'username': 'test_user3', 'password': 'test_password'}
        user_resource = json.loads(
            self.client().post('/user/register/', data=test_user).data
                .decode('utf-8').replace("'", "\"")
        )
        user_id = user_resource['id']

        # create a shoppinglist
        create_shoppinglist_resource = self.client().post(
            '/shoppinglist/', data={
                'title': 'Trip to Dubai',
                'user_id': user_id
            }
        )

        # get id of shoppinglist created
        json_shoppinglist_resource = json.loads(
            create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        shoppinglist_id = json_shoppinglist_resource['id']

        """test API can create shoppinglist item"""
        create_item_resource = self.client().post(
            '/shoppinglist/{}/items/'.format(shoppinglist_id),
            data={
                'name': 'Touring Shoes',
                'shoppinglist_id': shoppinglist_id
            }
        )
        self.assertEqual(create_item_resource.status_code, 201)
        self.assertIn('Touring Shoes', str(create_item_resource.data))

        # get id of item created
        json_item_resource = json.loads(
            create_item_resource.data.decode('utf-8').replace(
                "'", "\"")
        )
        item_id = json_item_resource['id']

        """test API can retrieve shoppinglist items"""
        get_item_resource = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id)
        )
        self.assertEqual(get_item_resource.status_code, 200)
        self.assertIn('Touring Shoes', str(get_item_resource.data))

        """test API can update shoppinglist item"""
        update_item_resource = self.client().put(
            '/shoppinglist/{}/items/{}'.format(shoppinglist_id, item_id),
            data={'name': 'Swimming floaters'}
        )
        self.assertEqual(update_item_resource.status_code, 200)

        # assert item was updated successfully
        items = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id)
        )
        self.assertIn('Swimming floaters', str(items.data))

        """test API can delete shoppinglist item"""
        delete_item_resource = self.client().delete(
            '/shoppinglist/{}/items/{}'.format(shoppinglist_id, item_id)
        )
        self.assertEqual(delete_item_resource.status_code, 200)

        # asert item has been deleted successfully
        items = self.client().get(
            '/shoppinglist/{}/items/'.format(shoppinglist_id)
        )
        self.assertNotIn('Swimming floaters', str(items.data))

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

        self.app = None
        self.client = None
