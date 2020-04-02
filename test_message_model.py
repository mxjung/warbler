"""Message model tests."""

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app
from unittest import TestCase

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

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()