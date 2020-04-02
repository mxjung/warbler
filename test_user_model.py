"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

# db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does User repr work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(str(u), f'<User #{u.id}: {u.username}, {u.email}>')
        self.assertNotEqual(str(u), f'<User #{u.username}: {u.id}, {u.email}>')

    def test_user_following(self):
        """Does User following method work?"""

        self.u2.following.append(self.u1)

        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()

        self.assertEqual(self.u2.is_following(self.u1), True)
        self.assertEqual(self.u1.is_following(self.u2), False)

    def test_user_followed_by(self):
        """Does User is_followed_by work correctly? """

        self.u2.followers.append(self.u1)

        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()

        self.assertEqual(self.u2.is_followed_by(self.u1), True)
        self.assertEqual(self.u1.is_followed_by(self.u2), False)

    def test_user_signup(self):
        """ Does User.signup work successfully? """

        User.signup("genna",
                    "genna@user.com",
                    "password",
                    "/static/default-pic.png"
                    )

        user3 = User.query.filter(User.username == "genna").one()
        self.assertEqual(user3.email, "genna@user.com")
        self.assertEqual(user3.image_url, "/static/default-pic.png")

    def test_invalid_signup(self):
        """ Test User.sign up does not work with invalid parameters"""
        try:
            User.signup("genna",
                        "genna@user.com",
                        "password",
                        )
        except TypeError:
            user = User.query.filter(User.username == "genna").all()
            self.assertEqual(user, [])

    def test_user_authenticate(self):
        """ Does User.authenticate work successfully? """

        User.signup("genna",
                    "genna@user.com",
                    "password",
                    "/static/default-pic.png"
                    )

        authentication = User.authenticate("genna",
                                           "password",
                                           )
        failed_authentication_password = User.authenticate("genna",
                                                           "failed",
                                                           )
        failed_authentication_username = User.authenticate("failed",
                                                           "password",
                                                           )

        self.assertNotEqual(authentication, False)
        self.assertEqual(failed_authentication_password, False)
        self.assertEqual(failed_authentication_username, False)
