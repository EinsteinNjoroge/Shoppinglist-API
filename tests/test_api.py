from unittest import TestCase
from app import launch_app
from app.models import db
from app.models import User
from app.models import Shoppinglists
from app.models import ShoppingListItems
from app.models import generate_random_id


config_mode = "testing"


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


# class UserTestCases(TestCase):
#     def setUp(self):
#         self.app = launch_app(config_mode)
#
#         with self.app.app_context():  # bind the app to the current context
#             db.create_all()  # create all tables
#
#         self.client = self.app.test_client
#
#         # self.json_user_resource = json.loads(
#         #     self.create_user_resource.data.decode('utf-8').replace(
#         #         "'", "\"")
#         # )
#
#     def test_api_can_create_user(self):
#         create_user_resource = self.client().post(
#             '/user/register/', data={
#                 'username': 'test_user',
#                 'password': 'test_password'
#             }
#         )
#
#         self.assertEqual(create_user_resource.status_code, 201)
#         self.assertIn('test_user', str(create_user_resource.data))
#
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
#
#     def tearDown(self):
#         with self.app.app_context():
#             # drop all tables
#             db.session.remove()
#             db.drop_all()
#
#         # reset all instance variables
#         self.app = None
#         self.client = None
#

class ShoppinglistTestCase(TestCase):
    """test cases for shoppinglist"""

    def setUp(self):
        self.app = launch_app(config_mode)

        with self.app.app_context():  # bind the app to the current context
            db.create_all()  # create all tables

        self.client = self.app.test_client

        json.loads(self.client().post('/user/register/',
                                      data={'username': 'test_user',
                                            'password': 'test_password'}
                                      ).data.decode('utf-8').replace("'", "\"")
                   )

        shoppinglist_id = self.json_shoppinglist_resource['id']

        self.create_shoppinglist_resource = self.client().post(
            '/shoppinglist/', data={
                'title': 'Back to school'
            }
        )

        self.get_shoppinglist_resource = self.client().get('/shoppinglist/')

        self.json_shoppinglist_resource = json.loads(
            self.create_shoppinglist_resource.data.decode('utf-8').replace(
                "'", "\"")
        )


    # def test_create_shoppinglist_endpoint(self):
    #     self.assertEqual(self.create_shoppinglist_resource.status_code, 201)
    #
    # def test_shoppinglist_created(self):
    #     self.assertIn('Back to school',
    #                   str(self.create_shoppinglist_resource.data))
    #
    # def test_get_shoppinglist_endpoint(self):
    #     self.assertEqual(self.get_shoppinglist_resource.status_code, 200)
    #
    # def test_api_can_retrieve_all_shoppinglists(self):
    #     self.assertIn('Back to school', str(self.get_shoppinglist_resource.data))
    #
    # def test_update_specific_shoppinglist_endpoint(self):
    #
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #
    #     # Update an already existing shoppinglist
    #     response = self.client().put(
    #         '/shoppinglist/{}'.format(shoppinglist_id),
    #         data={'title': "Weekend party"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_api_can_update_specific_shoppinglist(self):
    #
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #
    #     # Update an already existing shoppinglist
    #     self.client().put(
    #         '/shoppinglist/{}'.format(shoppinglist_id),
    #         data={'title': "Weekend party"}
    #     )
    #
    #     # assert shoppinglist was updated successfully
    #     shoppinglist = self.client().get(
    #         '/shoppinglist/{}'.format(shoppinglist_id)
    #     )
    #     self.assertIn('Weekend party', str(shoppinglist.data))
    #
    # def test_delete_specific_shoppinglist_endpoint(self):
    #
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #
    #     # Delete a shoppinglist
    #     response = self.client().delete('/shoppinglist/{}'.format(
    #         shoppinglist_id))
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_api_can_delete_specific_shoppinglist(self):
    #
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #
    #     # Delete a shoppinglist
    #     self.client().delete('/shoppinglist/{}'.format(
    #         shoppinglist_id))
    #
    #     # assert shoppinglist was deleted successfully
    #     shoppinglist = self.client().get(
    #         '/shoppinglist/{}'.format(shoppinglist_id)
    #     )
    #     self.assertEqual(shoppinglist.status_code, 404)
    #
    # def test_create_shoppinglist_item(self):
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #     create_item_resource = self.client().post(
    #         '/shoppinglist/{}/items/'.format(shoppinglist_id),
    #         data={'name': 'School Shoes'}
    #     )
    #     self.assertEqual(create_item_resource.status_code, 201)
    #
    #     self.assertIn('School Shoes', str(create_item_resource.data))
    #
    # def test_create_shoppinglist_item(self):
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #     create_item_resource = self.client().post(
    #         '/shoppinglist/{}/items/'.format(shoppinglist_id),
    #         data={'name': 'School Shoes'}
    #     )
    #     self.assertEqual(create_item_resource.status_code, 201)
    #
    #     self.assertIn('School Shoes', str(create_item_resource.data))
    #
    # def test_api_can_retrieve_items_in_a_shoppinglist(self):
    #     shoppinglist_id = self.json_shoppinglist_resource['id']
    #     self.client().post(
    #         '/shoppinglist/{}/items/'.format(shoppinglist_id),
    #         data={'name': 'School Shoes'}
    #     )
    #
    #     #  retrieve an existing shoppinglist
    #     shoppinglist_items = self.client().get(
    #         '/shoppinglist/{}/items/'.format(shoppinglist_id)
    #     )
    #     self.assertIn('School Shoes', str(shoppinglist_items.data))

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

        self.app = None
        self.client = None
        self.get_shoppinglist_resource = None
        self.create_shoppinglist_resource = None
