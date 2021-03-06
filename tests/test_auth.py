import os
import unittest
import sys

topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from Prescient import app, db
from Prescient.config import basedir


# Integration tests
class AuthorisationTests(unittest.TestCase):
    def setUp(self):  # sets up the database
        app.config["TESTING"] = True  # tests for assertions or exceptions
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
                                                os.path.join(basedir,
                                                             'test.db')
        self.app = app.test_client()  # this creates a test client for the app
        db.create_all()

    def tearDown(self):  # removes the database
        db.session.remove()
        db.drop_all()

    # Helper methods to create dummy post requests and store to test database
    def register_user(self, username, password, confirm):
        credentials = dict(username=username,
                           password=password,
                           confirm=confirm)
        return self.app.post("auth/register",
                             data=credentials,
                             follow_redirects=True)

    def login_user(self, username, password):
        credentials = dict(username=username,
                           password=password)
        return self.app.post("auth/login",
                             data=credentials,
                             follow_redirects=True)

    def logout_user(self):
        return self.app.get("auth/logout", follow_redirects=True)

    # tests
    def test_auth_urls(self):
        response_login = self.app.get("auth/login", follow_redirects=True)
        response_register = self.app.get("auth/register", follow_redirects=True)
        response_logout = self.app.get("auth/logout", follow_redirects=True)
        self.assertEqual(response_login.status_code, 200)
        self.assertEqual(response_register.status_code, 200)
        self.assertEqual(response_logout.status_code, 200)

    def test_valid_user_registration(self):
        response = self.register_user("RandomUser1!",
                                      "Testing123",
                                      "Testing123")
        self.assertIn(b"Your account has now been created!", response.data)

    def test_invalid_user_registration_wrong_confirm(self):
        response = self.register_user("RandomUser1!", "Testing13", "Testing31")
        self.assertIn(b"Passwords must match", response.data)

    def test_invalid_user_registration_duplicate_username(self):
        response = self.register_user("RandomUser2",
                                      "python99",
                                      "python99")
        response = self.register_user("RandomUser2",
                                      "python11",
                                      "python11")
        self.assertIn(b"That username is already registered.", response.data)

    def test_valid_login(self):
        self.register_user("RandomUser1!", "Testing123", "Testing123")
        response = self.login_user("RandomUser1!", "Testing123")
        self.assertIn(b"Welcome to Prescient Finance", response.data)

    def test_invalid_login_wrong_username(self):
        self.register_user("RandomUser1!", "Testing123", "Testing123")
        response = self.login_user("randomuser1!", "Testing123")
        self.assertNotIn(b"Welcome to Prescient Finance", response.data)

    def test_invalid_login_wrong_password(self):
        self.register_user("RandomUser1!", "Testing123", "Testing123")
        response = self.login_user("RandomUser1!", "Testing456")
        self.assertNotIn(b"Welcome to Prescient Finance", response.data)

    def test_logout(self):
        self.register_user("RandomUser1!", "Testing123", "Testing123")
        self.login_user("RandomUser1!", "Testing123")
        response = self.logout_user()
        self.assertIn(b"Sign In", response.data)


if __name__ == "__main__":
    unittest.main()
