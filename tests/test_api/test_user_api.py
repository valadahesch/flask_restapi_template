import unittest
import os

from flask import current_app
from app import create_app
from app.models import db


class TestUserAPI(unittest.TestCase):
    app = None
    app_context = None

    def dev_print(self, *args):
        if self.env == 'dev':
            print(args)

    @classmethod
    def setUpClass(cls):
        if cls.app:
            return

        env = os.environ.get('APP_ENV', 'dev')
        cls.app = create_app('app.config.%sConfig' % env.capitalize())
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        self.env = os.environ.get('APP_ENV', 'dev')

    def tearDown(self):
        db.session.remove()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

