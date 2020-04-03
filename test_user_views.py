"""Message model tests."""

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app
from unittest import TestCase
import sqlalchemy.exc

from models import db, User, Message, Follows

app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


class UserViewTests(TestCase):
    """Test User Views."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # u1 = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        User.signup("testuser", "test@test.com", "HASHED_PASSWORD", "image")

        # db.session.add(u1)
        db.session.commit()

        # self.u1_id = u1.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_signup_GET(self):
        """Get request to /signup"""

        with app.test_client() as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)
    
    def test_signup_POST(self):
        """Post request to /signup"""

        d = {"username": "maxjung", "password": "HASHED_PASSWORD", "email": "genna@gmail.com"}
        with app.test_client() as client:

            resp = client.post('/signup', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>@maxjung</p>', html)

    def test_invalid_signup_POST(self):
        """Post request to /signup with invalid password"""

        d = {"username": "maxjung", "password": "five", "email": "genna@gmail.com"}
        with app.test_client() as client:

            resp = client.post('/signup', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Tests for resp code 
            self.assertEqual(resp.status_code, 200)
            # Returns warning message for password
            self.assertIn('<span class="text-danger">Field must be at least 6 characters long.</span>', html)

    def test_invalid_duplicate_signup_POST(self):
        """Post request to /signup with invalid duplicate username"""

        d = {"username": "testuser", "password": "password", "email": "genna@gmail.com"}
        with app.test_client() as client:

            resp = client.post('/signup', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
       
            # Tests for resp code 
            self.assertEqual(resp.status_code, 200)
            # Returns warning message for duplicate username
            self.assertIn('<div class="alert alert-danger">Username already taken</div>', html)
        
    def test_login_GET(self):
        """Get request to /login"""

        with app.test_client() as client:
            resp = client.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

    def test_login_POST(self):
        """Post correct request to /login"""

        d = {"username": "testuser", "password": "HASHED_PASSWORD"}
        with app.test_client() as client:
            resp = client.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-success">Hello, testuser!</div>', html)

    def test_invalid_password_login_POST(self):
        """Post invalid request to /login with incorrect password"""

        d = {"username": "testuser", "password": "INVALID_PASSWORD"}
        with app.test_client() as client:
            resp = client.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Invalid credentials.</div>', html)

    def test_invalid_username_login_POST(self):
        """Post invalid request to /login with incorrect username"""

        d = {"username": "wronguser", "password": "HASHED_PASSWORD"}
        with app.test_client() as client:
            resp = client.post('/login', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Invalid credentials.</div>', html)

    # Finished post for login view method