from locust import HttpUser, task, between
import random
import datetime


class ProductAndOrderAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def get_products(self):
        """Get products sorted by price with pagination"""
        limit = random.choice([5, 10, 20, 50])
        offset = random.choice([0, 10, 20, 30, 40])
        direction = random.choice(["ASC", "DESC"])

        with self.client.get(
                f"/products/?limit={limit}&offset={offset}&direction={direction}",
                name="/products/",
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get products: {response.status_code}")

    @task(3)
    def get_popular_products(self):
        """Get the 10 most popular products"""
        with self.client.get(
                "/popular/",
                name="/popular/",
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get popular products: {response.status_code}")

    @task(2)
    def get_user_orders(self):
        """Get user orders within a date range with status filter"""
        user_id = random.randint(1, 100)

        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=random.randint(1, 365))

        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        status = random.choice(["Pending", "Completed", "Cancelled"])

        with self.client.get(
                f"/orders/?userId={user_id}&startDate={start_date_str}&endDate={end_date_str}&status={status}",
                name="/orders/",
                catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get user orders: {response.status_code}")
