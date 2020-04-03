"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

import sqlalchemy.exc
from app import app
from unittest import TestCase
from models import db, User, Message, Follows



# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test model for users."""

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

        db.session.add(u1)
        db.session.add(u2)

        db.session.commit()

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        db.session.add(self.u1)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_user_repr(self):
        """Does User repr work?"""

        db.session.add(self.u1)
        db.session.commit()

        self.assertEqual(
            str(self.u1), f'<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>')
        self.assertNotEqual(
            str(self.u1), f'<User #{self.u1.username}: {self.u1.id}, {self.u1.email}>')

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

    def test_invalid_signup_unique(self):
        """ Test User.sign up does not work with invalid parameters
            specifically for unique username"""

        User.signup("testuser",
                    "test@test.com",
                    "password",
                    "/static/default-pic.png"
                    )

        # 1) Pass commit as callback: self.assertRaises(exc.IntegrityError, db.session.commit)
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_invalid_signup_null_username(self):
        """Testing for Nullable username"""

        User.signup(None,
                    "test@test.com",
                    "password",
                    "/static/default-pic.png"
                    )
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_invalid_signup_null_email(self):
        """Testing for Nullable email"""

        User.signup("testuser",
                    None,
                    "password",
                    "/static/default-pic.png"
                    )
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            db.session.commit()

    def test_invalid_signup_null_password(self):
        """Testing for Nullable password"""

        with self.assertRaises(ValueError):
            User.signup("testuser",
                        "test@test.com",
                        None,
                        "/static/default-pic.png"
                        )
            db.session.commit()

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
