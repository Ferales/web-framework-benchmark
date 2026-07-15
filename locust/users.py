from locust import HttpUser, task, between
import json
import random
import string


class APIUser(HttpUser):
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.registered_users = []
        self.current_email = None
        self.current_password = None

    def generate_random_email(self):
        """Generate a random email address"""
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return f"{username}@example.com"

    def generate_random_password(self):
        """Generate a random password"""
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))

    @task(1)
    def register_user(self):
        """Register a new user"""
        self.current_email = self.generate_random_email()
        self.current_password = self.generate_random_password()

        user_data = {
            "email": self.current_email,
            "password": self.current_password,
            "name": f"User {random.randint(1000, 9999)}",
        }

        headers = {'Content-Type': 'application/json'}

        with self.client.post(
                "/register/",
                data=json.dumps(user_data),
                headers=headers,
                catch_response=True
        ) as response:
            if response.status_code == 201:
                self.registered_users.append((self.current_email, self.current_password))
                response.success()
            elif response.status_code == 400 and "już istnieje" in response.text:
                response.success()
            else:
                response.failure(f"Registration failed with status code: {response.status_code}")

    @task(3)
    def login_user(self):
        """Login with existing user or with random credentials"""
        headers = {'Content-Type': 'application/json'}

        if self.registered_users and random.random() < 0.8:
            email, password = random.choice(self.registered_users)
        else:
            email = self.generate_random_email()
            password = self.generate_random_password()

        login_data = {
            "email": email,
            "password": password
        }

        with self.client.post(
                "/login/",
                data=json.dumps(login_data),
                headers=headers,
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                if email not in [u[0] for u in self.registered_users]:
                    response.success()
                else:
                    response.failure("Login failed with registered credentials")
            else:
                response.failure(f"Login failed with unexpected status code: {response.status_code}")
