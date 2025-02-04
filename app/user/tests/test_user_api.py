"""
Test for user api
"""


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

#helper function to create user

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the api"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create user successfull"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name" : "Test Name"
        }

        res = self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code , status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

        # password is not in response
        self.assertNotIn("password", res.data)

    def test_user_with_email_exist_error(self):
        """test error returned if user with email exist"""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name" : "Test Name"
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code , status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_erro(self):
        """Test error is returned if password is less than 5 chars"""
        payload = {
            "email": "test@example.com",
            "password": "pw",
            "name" : "Test Name"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exist)


    def test_create_user_token(self):
        """Test generate token for valid credentials"""

        user_details = {
            "name" : "Test Name",
            "email" : "test@example.com",
            "password": "test-user-password123"
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password" : user_details["password"],
        }

        #the user must exist in the database , thats why we create it
        # before calling token service
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token" , res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(email="test@example.com", password = "goodpass")

        payload = {"email" : "test@example.com" , "password" : "badpass"}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token" , res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns error"""
        payload = {"email" : "test@example.com" , "password"  :""}

        res = self.client.post(TOKEN_URL , payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """test auth is requried for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication."""

    def setUp(self):
        #we create a user
        self.user = create_user(
            email = "test@example.com",
            password = "test12345",
            name= "Test Name"
        )

        self.client = APIClient()
        # we authenticate the created user
        # after force authenticate , every request will be authenticated
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retreive prfile for logged in user"""
        #returns details of the current authenticated user
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "email" : self.user.email,
            "name"  : self.user.name
        })

    def test_post_me_not_allowed(self):
        """test posting  to ME endpoint is not allowed"""
        res = self.client.post(ME_URL ,{})
        self.assertEqual(res.status_code , status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test update the user profile"""

        payload = {"name" : "Updated name", "password" : "newpassword123"}

        res = self.client.patch(ME_URL, payload)

        # we need to refresh the db
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
