from django.contrib.auth import get_user_model
from django.test import TestCase
from django.contrib.auth import login

class UsersManagersTests(TestCase):

    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        with self.assertRaises(ValueError):
            # checks error with no email
            User.objects.create_user(**{})
        with self.assertRaises(ValueError):
            # checks error with no password or empty one
            User.objects.create_user(email="normal@user.com", password="")

    def test_login(self):
        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="foo")
        
        # checks login is not possible before validating the user
        self.client.login(username=user.email, password="foo")
        self.assertFalse(user.is_authenticated)

        # checks login is only possible after validating the user
        user.validated=True
        user.save(update_fields=['validated',])
        self.client.login(username=user.email, password="foo")
        self.assertTrue(user.is_authenticated)


    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(**{'email':"super@user.com", 'password':"foo"})
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)