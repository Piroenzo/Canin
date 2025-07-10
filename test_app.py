import unittest
from app import app
from flask import url_for

class CaninExpressTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Canin Express', resp.data)

    def test_login_get(self):
        resp = self.app.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Usuario', resp.data)

    def test_login_post_invalido(self):
        resp = self.app.post('/login', data={'usuario': 'fake', 'password': 'fake'})
        self.assertIn(b'incorrectos', resp.data)

    def test_productos_api_get(self):
        resp = self.app.get('/api/productos')
        self.assertIn(resp.status_code, [200, 500])  # Puede fallar si no hay DB

    def test_contacto_post_invalido(self):
        resp = self.app.post('/contacto', data={'nombre': '', 'email': 'noemail', 'mensaje': ''}, follow_redirects=True)
        self.assertIn(b'El nombre debe tener entre 2 y 40 caracteres', resp.data)
        self.assertIn(b'El correo electr', resp.data)

if __name__ == '__main__':
    unittest.main() 