import os
import subprocess
import sys
import time

test_blocks = {
    "crud": "crud.py",
    "files": "files.py",
    "users": "users.py",
    "products_orders": "products_orders.py",
}

test_cases = {
    "crud": [
        ("1.1", 50, 2, 180),
        ("1.2", 250, 8, 360),
        ("1.3", 500, 15, 720),
    ],
    "users": [
        ("2.1", 25, 2, 120),
        ("2.2", 100, 5, 300),
        ("2.3", 250, 10, 600),
    ],
    "files": [
        ("3.1", 15, 1, 120),
        ("3.2", 35, 3, 300),
        ("3.3", 75, 5, 600),
    ],
    "products_orders": [
        ("4.1", 30, 2, 240),
        ("4.2", 80, 4, 480),
        ("4.3", 200, 8, 900),
    ],
}

frameworks = {
    "django": "http://localhost:8000/api",
    "aspnet": "http://localhost:5281/api",
    "express": "http://localhost:3000/api",
}


def refresh_database():
    print("\nOdświeżanie bazy danych...")
    subprocess.run(
        [sys.executable, "../database/spawn_container.py"],
        check=True,
    )
    time.sleep(5)


def run_test(
    script_name,
    test_id,
    users,
    spawn_rate,
    duration,
    host,
    framework_name,
):
    print(
        f"[{framework_name.upper()}] Test {test_id} ({script_name}) - "
        f"{users} użytk., {duration}s..."
    )

    output_prefix = (
        f"results/{framework_name}/test_{test_id.replace('.', '_')}"
    )
    html_report = f"{output_prefix}.html"

    os.makedirs(f"results/{framework_name}", exist_ok=True)

    subprocess.run(
        [
            "locust",
            "-f",
            script_name,
            "--headless",
            "-u",
            str(users),
            "-r",
            str(spawn_rate),
            "--run-time",
            f"{duration}s",
            "--csv",
            output_prefix,
            "--csv-full-history",
            "--html",
            html_report,
            "--host",
            host,
        ]
    )


def main():
    for framework_name, host in frameworks.items():
        print(f"\n========== FRAMEWORK: {framework_name.upper()} ==========")

        for block_name, script in test_blocks.items():
            print(f"\n=== Blok: {block_name.upper()} ===")

            refresh_database()

            for test_id, users, spawn_rate, duration in test_cases[block_name]:
                run_test(
                    script,
                    test_id,
                    users,
                    spawn_rate,
                    duration,
                    host,
                    framework_name,
                )


if __name__ == "__main__":
    main()