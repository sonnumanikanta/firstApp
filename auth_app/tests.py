from rest_framework.test import APIClient
from django.test import SimpleTestCase
from django.urls import reverse

class AuthTests(SimpleTestCase):
    def setUp(self):
        # ✅ Use APIClient instead of APITestCase
        self.client = APIClient()

    def test_signup(self):
        url = reverse('signup')
        # ✅ unique username/email ताकि duplicate error न आए
        data = {"username": "signup_user1", "email": "signup1@example.com", "password": "Test@123"}
        response = self.client.post(url, data, format='json')
        print("Signup response:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)

    def test_login(self):
        # पहले signup करें
        signup_url = reverse('signup')
        self.client.post(signup_url, {"username": "login_user1", "email": "login1@example.com", "password": "Test@123"}, format='json')

        # फिर login करें
        login_url = reverse('login')
        response = self.client.post(login_url, {"username": "login_user1", "password": "Test@123"}, format='json')
        print("Login response:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_verify(self):
        # signup + login से access token लें
        signup_url = reverse('signup')
        self.client.post(signup_url, {"username": "verify_user1", "email": "verify1@example.com", "password": "Verify@123"}, format='json')
        login_url = reverse('login')
        login_response = self.client.post(login_url, {"username": "verify_user1", "password": "Verify@123"}, format='json')
        access_token = login_response.data.get("access")

        # ✅ verify endpoint पर भेजें (use 'token' key)
        verify_url = reverse('token_verify')
        response = self.client.post(verify_url, {"token": access_token}, format='json')
        print("Verify response:", response.data)
        # Debugging के लिए पहले response print होगा
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.get("valid"))

    def test_eventform_create(self):
        url = reverse('event_form')
        data = {
            "event_name": "Birthday Party",
            "contact_number": "9876543210",
            "photo": "",
            "event_date": "2025-12-31T18:00:00Z"
        }
        response = self.client.post(url, data, format='json')
        print("EventForm create response:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)

    def test_eventform_list(self):
        url = reverse('event_form')
        response = self.client.get(url, format='json')
        print("EventForm list response:", response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)