from django.test import TestCase, Client
from openra.views import index

HTTP_HOST = ''

class TestWithNoData(TestCase):

    def test_index(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_maps(self):
        c = Client()
        response = c.get('/maps/')
        self.assertEqual(response.status_code, 200)

    def test_sign_in(self):
        c = Client()
        response = c.get('/login/', HTTP_HOST=HTTP_HOST)
        print(response.content)
        self.assertEqual(response.status_code, 200)


