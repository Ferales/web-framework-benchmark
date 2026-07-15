import base64
import os
import pdb
import random
from locust import HttpUser, task, between
from locust.exception import RescheduleTask


class FileAPIImageUser(HttpUser):
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uploaded_file_ids = {}
        self.images_folder = "test_images"

        self.test_images = [
            "test_image_50kb.jpg",
            "test_image_500kb.jpg",
            "test_image_5mb.jpg",
            "test_image_10mb.jpg"
        ]

        self.available_images = []

    def on_start(self):
        """Called when a user starts before any task is scheduled"""
        self._verify_test_images()

        if not self.available_images:
            print("WARNING: No test images found. Please ensure test_images folder contains the required files.")
            return

        for image_name in self.available_images:
            file_id = self._upload_specific_image(image_name)
            if file_id:
                self.uploaded_file_ids[image_name] = file_id
                print(f"Initialized with {image_name}: ID {file_id}")

    def _verify_test_images(self):
        """Check which test images exist and report their sizes"""
        print("\n--- Test Image Verification ---")

        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)
            print(f"Created {self.images_folder} directory. Please add the following test images:")
            for img in self.test_images:
                print(f"  - {img}")
            return

        for image_name in self.test_images:
            image_path = os.path.join(self.images_folder, image_name)
            if os.path.exists(image_path):
                size_bytes = os.path.getsize(image_path)
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024

                if size_mb >= 1:
                    print(f"Found {image_name}: {size_mb:.2f} MB")
                else:
                    print(f"Found {image_name}: {size_kb:.2f} KB")

                self.available_images.append(image_name)
            else:
                print(f"Missing {image_name} - this test image won't be used")

        print("-----------------------------\n")

    def _upload_specific_image(self, image_name):
        """Helper method to upload a specific image file and return its ID"""
        image_path = os.path.join(self.images_folder, image_name)
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None

        try:
            with open(image_path, "rb") as image_file:
                files = {'file_data': (image_name, image_file, 'image/jpeg')}
                data = {'name': image_name}

                response = self.client.post("/upload_file/", files=files, data=data,
                                            name=f"/upload_file/ ({self._get_size_category(image_name)})")

                if response.status_code == 201 or response.status_code == 200:
                    json_response = response.json()
                    file_id = json_response.get('fileId') or json_response.get('id')
                    return file_id
                else:
                    print(f"Upload failed with status {response.status_code}")
                    return None

        except Exception as e:

            return None

    def _get_size_category(self, image_name):
        """Extract size category from image name for better metrics grouping"""
        if "50kb" in image_name.lower():
            return "Small-50KB"
        elif "500kb" in image_name.lower():
            return "Medium-500KB"
        elif "5mb" in image_name.lower():
            return "Large-5MB"
        elif "10mb" in image_name.lower():
            return "XLarge-10MB"
        else:
            return "Unknown"

    @task(3)
    def upload_random_image(self):
        """Task to upload a random image file"""
        if not self.available_images:
            return

        image_name = random.choice(self.available_images)
        file_id = self._upload_specific_image(image_name)

        if file_id:
            self.uploaded_file_ids[image_name] = file_id

    @task(5)
    def download_random_file(self):
        """Task to download a previously uploaded file"""
        if not self.uploaded_file_ids:
            raise RescheduleTask("No files available to download")

        image_name = random.choice(list(self.uploaded_file_ids.keys()))
        file_id = self.uploaded_file_ids[image_name]

        try:
            response = self.client.get(
                f"/download_file/{file_id}/",
                name=f"/download_file/ ({self._get_size_category(image_name)})"
            )

            if response.status_code == 200:
                json_response = response.json()
                assert "fileData" in json_response, "Response missing fileData field"

                try:
                    base64.b64decode(json_response["fileData"])
                except Exception as e:
                    print(f"Invalid Base64 data: {str(e)}")
            else:
                print(f"Failed to download {image_name} with status {response.status_code}")

        except Exception as e:
            print(f"Error downloading file {file_id} ({image_name}): {str(e)}")
