'''Tests for api endpoints'''
import json

# local imports
from . import BaseTestClass


class TestHomeResource(BaseTestClass):
	'''Test for Home Resources'''
	def test_welcome_message(self):
		'''test welcome message can be displayed'''
		res = self.client.get('/api/v2/home')
		self.assertEqual(200, res.status_code)

	def test_get_profile(self):
		access_token = self.login_user()
		headers = dict(Authorization="Bearer {}".format(access_token))

		res = self.client.get('/api/v2/profile', headers=headers)
		self.assertEqual(200, res.status_code)
		self.assertTrue(json.loads(res.data)['profile'])