'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass


class TestHomeResource(BaseTestClass):
    def test_welcome_message(self):
        res = self.client.get('/api/v1/')
        self.assertEqual(200, res.status_code)