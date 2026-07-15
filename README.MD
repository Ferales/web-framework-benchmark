# Performance Comparison of Web Frameworks

This project compares the performance of three web frameworks: **ASP.NET Core**, **Django**, and **Node.js (Express)**. Applications are containerized using Docker, while load tests are executed with Locust. Before each benchmark scenario, the PostgreSQL database is automatically reset and populated with identical test data to ensure consistent testing conditions.

## Requirements

- Docker Engine with Docker Compose
- Python 3.13+

## Getting Started

### 1. Build the Docker images

Run this command only the first time or after modifying the application source code.

```bash
docker compose -f docker-compose.apps.yml build
```

### 2. Start the PostgreSQL container

```bash
docker compose -f database/docker-compose.yml up -d
```

### 3. Start the application containers

```bash
docker compose -f docker-compose.apps.yml up -d
```

### 4. Set up the Python environment

```bash
cd locust

python -m venv .venv
```

Activate it (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 5. Run the benchmarks

```bash
python automate_benchmark.py
```

The benchmark script automatically:

- resets the PostgreSQL database,
- recreates the database schema,
- loads the test data,
- executes all benchmark scenarios.

Benchmark results are saved to:

```text
results/
```