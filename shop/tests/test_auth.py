from django.test import TestCase
from django.urls import reverse
 


class AuthTest(TestCase):
    """Test cases for authentication-related views

    Args:
        TestCase (_type_): _Django TestCase class
    """
    def test_user_registration_view(self):
        """Test the user registration view
        """
        response = self.client.post(reverse('register'), {
            'username': 'biscuit_lover',
            'email': 'test@example.com',
            'password1': 'Activation6421',
            'password2': 'Activation6421'
        }, follow=True)
        self.assertEqual(response.status_code, 200)                     
        self.assertRedirects(response, reverse('home'))                 #type: ignore

    def test_customer_profile_created_with_user(self):
        """Test that a CustomerProfile is created when a new user registers
        """
        from shop.models import CustomerProfile 
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(
            username='biscuit_lover',
            password='Activation6421',
            email='test@example.com'
        )
        profile_exists = CustomerProfile.objects.filter(user=user).exists()
        self.assertTrue(profile_exists, 'No profile created with this user')
        
    def test_login_user(self):
        """Test the user login view
        """
        response = self.client.post(reverse('login'), {
            'username': 'biscuit_lover',
            'password': 'Activation6421'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

class AdminSecurityTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.client_user = User.objects.create_user(username='client', password='Activation6421')
        self.staff_user = User.objects.create_user(username='admin_staff', password='Activation6421', is_staff=True)

    def test_anonymous_user_cannot_access_admin(self):
        """Un utilisateur non connecté est redirigé vers le login admin"""
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url) #type: ignore

    def test_regular_user_cannot_access_admin(self):
        """Un client connecté mais non-staff ne peut pas voir l'admin"""
        self.client.login(username='client', password='Activation6421')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_access_admin(self):
        """Un membre du staff peut accéder à l'index admin"""
        self.client.login(username='admin_staff', password='Activation6421')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)