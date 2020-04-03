"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from unittest import TestCase
from models import db, connect_db, Message, User
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser.id = 100

        self.testuser2 = User.signup(username="testuser2",
                                    email="test@test2.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser2.id = 200
        
        db.session.commit()
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
    
    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_invalid_add_message(self):
        """Can use add a message if you're not logged in?"""

        with self.client as client:
            resp = client.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Make sure it redirects (follow redirect)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)


    def test_delete_message(self):
        """Can use delete a message?"""
        newMsg = Message(text="this works")
        newMsg.id = 16
        newMsg.user_id = self.testuser.id

        db.session.add(newMsg)
        db.session.commit()

        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/16/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            m = Message.query.get(16)
            self.assertIsNone(m)

    def test_invalid_delete_message(self):
        """Can use delete a message if you're not logged in?"""

        newMsg = Message(text="this works")
        newMsg.id = 16
        newMsg.user_id = self.testuser.id

        db.session.add(newMsg)
        db.session.commit()

        with self.client as client:
            resp = client.post('/messages/16/delete', follow_redirects=True)            
            html = resp.get_data(as_text=True)

            # Make sure it redirects (follow redirect)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_like_message(self):
        """Can use like a message (written by someone else)?"""

        newMsg = Message(text="this works")
        newMsg.id = 16
        newMsg.user_id = self.testuser2.id

        db.session.add(newMsg)
        db.session.commit()
       
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/16/like', follow_redirects=True)
            resp_likes = c.get('/users/100/likes')

            # Make sure it redirects (follow redirect)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp_likes.status_code, 200)
            self.assertIn('<p>this works</p>', str(resp_likes.data))