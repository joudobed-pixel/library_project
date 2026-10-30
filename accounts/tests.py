from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_login_profile(self):
        register = self.client.post("/api/register/", {
            "username": "student1", "email": "student1@example.com", "password": "StrongPass!234",
        }, format="json")
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", register.data)
        # The password is stored hashed, not as plain text.
        self.assertNotEqual(User.objects.get(username="student1").password, "StrongPass!234")

        login = self.client.post("/api/login/", {"username": "student1", "password": "StrongPass!234"},
                                 format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        profile = self.client.get("/api/profile/")
        self.assertEqual(profile.status_code, status.HTTP_200_OK)
        self.assertEqual(profile.data["username"], "student1")

        refresh = self.client.post("/api/token/refresh/", {"refresh": login.data["refresh"]}, format="json")
        self.assertEqual(refresh.status_code, status.HTTP_200_OK)

    def test_profile_requires_login(self):
        self.assertEqual(self.client.get("/api/profile/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        self.assertEqual(self.client.get("/api/profile/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_weak_password_rejected(self):
        response = self.client.post("/api/register/", {"username": "u2", "password": "123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
