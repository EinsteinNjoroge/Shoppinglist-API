from unittest import TestCase
from flask import json
from app import create_instance_of_flask_api
from app import db


class ShoppinglistTestCase(TestCase):
    """test cases for my shoppinglist api"""

    def setUp(self):
        self.app = create_instance_of_flask_api(config_mode="testing")

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

        self.client = self.app.test_client
        self.create_resource = self.client().post(
            '/shoppinglist/', data={'title': 'Back to school'})
        self.get_resource = self.client().get('/shoppinglist/')
        # self.json_resource = json.load(
        #     self.create_resource.data.decode('utf-8').replace("'", "\"")
        # )

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

        # reset all instance variables
        self.app = None
        self.client = None
        # self.json_resource = None
        self.get_resource = None
        self.create_resource = None

    def test_shoppinglist_endpoint(self):
        self.assertEqual(self.create_resource.status_code, 201)

    def test_shoppinglist_created(self):
        self.assertIn('Back to school', str(self.create_resource.data))

    def test_get_shoppinglist_endpoint(self):
        self.assertEqual(self.get_resource.status_code, 200)

    def test_api_can_retrieve_all_shoppinglists(self):
        self.assertIn('Back to school', str(self.get_resource.data))

    # def test_api_can_retrieve_specific_shoppinglist(self):
    #     shoppinglist_id = self.json_resource['id']
    #
    #     #  retrieve an existing shoppinglist
    #     shoppinglist = self.client().get(
    #         '/shoppinglist/{}'.format(shoppinglist_id)
    #     )
    #     self.assertIn('Back to school', str(shoppinglist.data))
    #
    # def test_update_specific_shoppinglist_endpoint(self):
    #     shoppinglist_id = self.json_resource['id']
    #
    #     # Update an already existing shoppinglist
    #     response = self.client().put(
    #         '/shoppinglist/{}'.format(shoppinglist_id),
    #         data={'title': "Weekend party"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_api_can_update_specific_shoppinglist(self):
    #     shoppinglist_id = self.json_resource['id']
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
    #     shoppinglist_id = self.json_resource['id']
    #
    #     # Delete a shoppinglist
    #     response = self.client().delete('/shoppinglist/{}'.format(
    #         shoppinglist_id))
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_api_can_delete_specific_shoppinglist(self):
    #     shoppinglist_id = self.json_resource['id']
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
