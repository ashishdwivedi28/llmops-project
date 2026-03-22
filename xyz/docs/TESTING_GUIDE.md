# LLMOps Testing & Quality Guide

This document explains the testing infrastructure, quality tools, and workflows established for the LLMOps backend.

## 1. Testing Philosophy

We follow a "Safety First" approach for this production pipeline:
*   **Static Analysis:** Catch bugs before running code (Type checking, Linting).
*   **Unit Tests:** Verify individual components (Config, Pipelines, Routing) in isolation.
*   **Integration Tests:** Verify the API endpoints (`/invoke`) work as a whole system.
*   **Coverage:** We aim for high code coverage (70% target) to ensure reliability.

---

## 2. Tools Installed

We use a modern Python quality stack installed via `requirements-dev.txt`:

| Tool | Purpose | Why we use it |
| :--- | :--- | :--- |
| **Pytest** | Test Runner | Standard, powerful, plugin-rich testing framework. |
| **Pytest-Cov** | Code Coverage | Measures which lines of code were executed during tests. |
| **Pytest-Asyncio** | Async Testing | Essential for testing FastAPI's async endpoints. |
| **Pytest-Mock** | Mocking | Easily replace external calls (like Vertex AI) with fake data. |
| **Ruff** | Linter & Formatter | Extremely fast replacement for Flake8, Black, and Isort. |
| **Mypy** | Type Checker | Enforces static typing (e.g., `str` vs `int`) to prevent runtime errors. |
| **HTTPX** | Test Client | Used by `TestClient` to make requests to our FastAPI app. |

---

## 3. How to Run Tests

We have a `Makefile` to simplify running commands. You should run these from the `xyz/` folder.

### 3.1. One-Command Check (Recommended)
This runs formatting, linting, type checking, and all tests in one go. Run this before pushing code.
```bash
make check
make test
```

### 3.2. Running Specific Suites
*   **Unit Tests:** Fast tests for individual logic.
    ```bash
    make test-unit
    ```
*   **Integration Tests:** Slower tests hitting the API endpoints.
    ```bash
    make test-integration
    ```
*   **Run All Tests (Verbose):**
    ```bash
    make test
    ```

### 3.3. Checking Code Coverage
To see exactly which lines are covered by tests:
```bash
make coverage
```
This will print a report in the terminal and generate an HTML report in `xyz/htmlcov/`. Open `xyz/htmlcov/index.html` in your browser to explore it.

---

## 4. Linting & Formatting

We use **Ruff** to keep code clean and consistent.

*   **Check for issues:**
    ```bash
    make lint
    ```
*   **Auto-fix issues (Format code):**
    ```bash
    make format
    ```
*   **Type Checking (Mypy):**
    This ensures you aren't passing the wrong data types (e.g., passing a `None` where a `string` is expected).
    ```bash
    # (Included in 'make check')
    ./venv/bin/mypy app/ utils/ --ignore-missing-imports
    ```

---

## 5. Configuration Files

*   **`pyproject.toml`**: The main config file.
    *   `[tool.pytest.ini_options]`: Configures pytest flags and discovery.
    *   `[tool.coverage.run]`: Tells coverage what files to track.
    *   `[tool.mypy]`: Settings for strictness of type checking.
*   **`.ruff.toml`**: Configures linting rules (line length, import sorting, ignored errors).

## 6. How to Write New Tests

1.  **Unit Tests:**
    *   Create a file in `tests/unit/test_your_module.py`.
    *   Import the class/function you want to test.
    *   Use `pytest.fixture` (from `tests/conftest.py`) to get mock configs.
    *   Use `unittest.mock.patch` to fake external calls (like LLM APIs).

    ```python
    def test_my_function(mock_config):
        # ... test logic ...
        assert result == "expected"
    ```

2.  **Integration Tests:**
    *   Create a file in `tests/integration/`.
    *   Use the `test_client` fixture to send requests to the API.

    ```python
    def test_api_call(test_client):
        response = test_client.post("/invoke", json={...})
        assert response.status_code == 200
    ```
