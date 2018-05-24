'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass


class TestHomeResource(BaseTestClass):
	'''Test for Home Resources'''
	def test_welcome_message(self):
		'''test welcome message can be displayed'''
		res = self.client.get('/api/v1/')
		self.assertEqual(200, res.status_code)
