from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountAuthTests(APITestCase):
    def test_user_register_login_and_me(self):
        register_resp = self.client.post(
            "/api/auth/user/register/",
            {
                "username": "user1",
                "email": "user1@example.com",
                "password": "Passw0rd!",
            },
            format="json",
        )
        self.assertEqual(register_resp.status_code, status.HTTP_201_CREATED)

        login_resp = self.client.post(
            "/api/auth/user/login/",
            {"username": "user1", "password": "Passw0rd!"},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access = login_resp.data.get("access")
        self.assertTrue(access)

        me_resp = self.client.get(
            "/api/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data.get("role"), "user")
        self.assertFalse(me_resp.data.get("is_staff"))

    def test_admin_login_rejects_non_staff(self):
        user = User.objects.create_user(username="user2", password="Passw0rd!")
        self.assertFalse(user.is_staff)

        resp = self.client.post(
            "/api/auth/admin/login/",
            {"username": "user2", "password": "Passw0rd!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_rejects_admin(self):
        admin = User.objects.create_user(
            username="admin1",
            password="Passw0rd!",
            is_staff=True,
        )
        self.assertTrue(admin.is_staff)

        resp = self.client.post(
            "/api/auth/user/login/",
            {"username": "admin1", "password": "Passw0rd!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_register_requires_admin(self):
        resp = self.client.post(
            "/api/auth/admin/register/",
            {
                "username": "admin2",
                "email": "admin2@example.com",
                "password": "Passw0rd!",
            },
            format="json",
        )
        self.assertIn(resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        User.objects.create_user(
            username="superadmin",
            password="Passw0rd!",
            is_staff=True,
        )
        login_resp = self.client.post(
            "/api/auth/admin/login/",
            {"username": "superadmin", "password": "Passw0rd!"},
            format="json",
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access = login_resp.data.get("access")
        self.assertTrue(access)

        create_resp = self.client.post(
            "/api/auth/admin/register/",
            {
                "username": "admin3",
                "email": "admin3@example.com",
                "password": "Passw0rd!",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        new_admin = User.objects.get(username="admin3")
        self.assertTrue(new_admin.is_staff)
        self.assertFalse(new_admin.is_superuser)
