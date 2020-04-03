"""Message model tests."""

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
from unittest import TestCase
import sqlalchemy.exc

from models import db, User, Message, Follows


db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        msg = Message(text="New test message")
        msg.id = 100

        db.session.add(u1)
        u1.messages.append(msg)

        db.session.commit()

        self.u1 = u1
        self.u1_id = u1.id
        self.msg_id = msg.id

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_msg_repr(self):
        """Does Message repr work?"""

        msg = Message.query.get(self.msg_id)
       
        self.assertEqual(
            str(msg), f"<Message #{self.msg_id} by {msg.user_id} on {msg.timestamp}: {msg.text}>")
        self.assertNotEqual(
            str(msg), f"<Message #{self.msg_id} by {msg.user_id} on pancakes: {msg.text}>")

    def test_user_msg_relationship(self):
        """Does User to Message relationship work?"""

        user_msg = self.u1.messages
        msg = Message.query.get(self.msg_id)
        self.assertIn(msg, user_msg)

    def test_msg_user_relationship(self):
        """Does Message to User relationship work?"""

        msg = Message.query.get(self.msg_id)
        msg_user = msg.user
        self.assertEqual(self.u1, msg_user)

    def test_invalid_msg_create(self):
        """Does creating invalid Message Error?"""
        
        msg = Message(text=None)
        db.session.add(msg)
    
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

        