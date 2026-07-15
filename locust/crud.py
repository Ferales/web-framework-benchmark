"""
User CRUD operations test cases for the benchmark application.
This file contains all the test cases related to User model CRUD operations.
"""
import random
import string
from locust import HttpUser, task, between, TaskSet


class UserCRUDTaskSet(TaskSet):
    """TaskSet containing User CRUD operations"""

    def on_start(self):
        """Initialize user data and IDs store."""
        self.user_ids = []

    def _generate_random_user(self):
        """Generate random user data."""
        random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
        return {
            "name": f"User {random_string}",
            "email": f"user_{random_string}@example.com",
            "password": f"pass_{random_string}_{random.randint(1000, 9999)}",
            "age": random.randint(18, 99)
        }

    @task(3)
    def create_user(self):
        """Create a new user."""
        user_data = self._generate_random_user()

        with self.client.post(
                "/users/",
                json=user_data,
                catch_response=True,
                name="/users/ - Create User"
        ) as response:
            if response.status_code == 201:
                user_id = response.json().get('id')
                if user_id:
                    self.user_ids.append(user_id)
            else:
                response.failure(f"Failed to create user: {response.status_code}")

    @task(4)
    def get_user_by_id(self):
        """Get a specific user by ID."""
        if not self.user_ids:
            return

        user_id = random.choice(self.user_ids)
        with self.client.get(
                f"/users/{user_id}/",
                catch_response=True,
                name="/users/{id}/ - Get User by ID"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get user {user_id}: {response.status_code}")
                if response.status_code == 404:
                    self.user_ids.remove(user_id)

    @task(2)
    def update_user(self):
        """Update an existing user."""
        if not self.user_ids:
            return

        user_id = random.choice(self.user_ids)
        update_data = self._generate_random_user()
        update_data["id"] = user_id

        with self.client.put(
                f"/users/{user_id}/",
                json=update_data,
                catch_response=True,
                name="/users/{id}/ - Update User"
        ) as response:
            if response.status_code not in [200, 204]:
                response.failure(f"Failed to update user {user_id}: {response.status_code}")
                if response.status_code == 404:
                    self.user_ids.remove(user_id)

    @task(1)
    def delete_user(self):
        """Delete a user."""
        if not self.user_ids:
            return

        user_id = random.choice(self.user_ids)

        with self.client.delete(
                f"/users/{user_id}/",
                name="/users/{id}/ - Delete User",
                catch_response=True
        ) as response:
            if response.status_code in [200, 204]:
                self.user_ids.remove(user_id)
            else:
                response.failure(f"Failed to delete user {user_id}: {response.status_code}")
                if response.status_code == 404:
                    self.user_ids.remove(user_id)


class UserLifecycleTaskSet(TaskSet):
    """
    TaskSet for testing the full lifecycle of user records:
    1. Create users
    2. Fetch them several times
    3. Update them
    4. Finally delete them
    """

    def _generate_random_user(self):
        random_string = ''.join(random.choices(string.ascii_lowercase, k=8))
        return {
            "name": f"Fixed User {random_string}",
            "email": f"fixed_{random_string}@example.com",
            "password": f"fixed_pass_{random_string}_{random.randint(1000, 9999)}",
            "age": random.randint(18, 99)
        }

    @task
    def user_lifecycle(self):
        user_data = self._generate_random_user()

        with self.client.post(
                "/users/",
                json=user_data,
                catch_response=True,
                name="Lifecycle - 1. Create User"
        ) as response:
            if response.status_code == 201:
                user_id = response.json().get('id')
                if not user_id:
                    response.failure("User created but no ID returned")
                    return
            else:
                response.failure(f"Failed to create user: {response.status_code}")
                return

        for i in range(3):
            with self.client.get(
                    f"/users/{user_id}/",
                    catch_response=True,
                    name=f"Lifecycle - 2. Get User (#{i + 1})"
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Failed to get user: {response.status_code}")
                    return

        update_data = self._generate_random_user()
        update_data["id"] = user_id

        with self.client.put(
                f"/users/{user_id}/",
                json=update_data,
                catch_response=True,
                name="Lifecycle - 3. Update User"
        ) as response:
            if response.status_code not in [200, 204]:
                response.failure(f"Failed to update user: {response.status_code}")
                return

        with self.client.get(
                f"/users/{user_id}/",
                catch_response=True,
                name="Lifecycle - 4. Get Updated User"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get updated user: {response.status_code}")
                return

        with self.client.delete(
                f"/users/{user_id}/",
                catch_response=True,
                name="Lifecycle - 5. Delete User"
        ) as response:
            if response.status_code not in [200, 204]:
                response.failure(f"Failed to delete user: {response.status_code}")


class ReadOnlyTaskSet(TaskSet):
    """TaskSet focused on read operations to test database read performance."""

    @task(5)
    def get_user_by_id(self):
        user_id = random.randint(1, 100)
        with self.client.get(
                f"/users/{user_id}/",
                catch_response=True,
                name="HighVolume - Get User by ID"
        ) as response:
            if response.status_code != 200 and response.status_code != 404:
                response.failure(f"Error getting user {user_id}: {response.status_code}")


class UserCRUDUser(HttpUser):
    """User class for basic CRUD operations"""
    wait_time = between(1, 3)
    tasks = [UserCRUDTaskSet]


class UserLifecycleUser(HttpUser):
    """User class for testing complete user lifecycle"""
    wait_time = between(1, 2)
    tasks = [UserLifecycleTaskSet]


class HighVolumeReadUser(HttpUser):
    """User class focused on read operations"""
    wait_time = between(0.1, 1)
    tasks = [ReadOnlyTaskSet]