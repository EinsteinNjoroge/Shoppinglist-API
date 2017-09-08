from unittest import TestCase
from app import create_instance_of_flask_api
from app import db


class ShoppinglistTestCase(TestCase):
    """test cases for my shoppinglist api"""

    def setUp(self):
        self.app = create_instance_of_flask_api(configuration_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'title': 'Back to school'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()
