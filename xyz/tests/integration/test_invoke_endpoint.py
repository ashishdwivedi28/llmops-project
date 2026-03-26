"""Integration tests for the POST /invoke endpoint."""


class TestInvokeEndpoint:
    """Full request/response cycle tests using the FastAPI test client."""

    def test_health_endpoint_returns_ok(self, test_client):
        """GET / should return status=ok."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_invoke_mock_app_returns_200(self, test_client):
        """POST /invoke with mock_app should return 200 with all fields."""
        response = test_client.post(
            "/invoke", json={"app_id": "mock_app", "user_input": "Hello world"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "output" in data
        assert "pipeline_executed" in data
        assert "latency_ms" in data
        assert isinstance(data["latency_ms"], float)

    def test_invoke_invalid_app_id_returns_404(self, test_client):
        """POST /invoke with unknown app_id should return 404."""
        response = test_client.post(
            "/invoke", json={"app_id": "nonexistent_app_xyz", "user_input": "Hello"}
        )
        assert response.status_code == 404

    def test_invoke_missing_user_input_returns_422(self, test_client):
        """POST /invoke with missing user_input should return 422."""
        response = test_client.post("/invoke", json={"app_id": "mock_app"})
        assert response.status_code == 422

    def test_invoke_response_contains_task_detection(self, test_client):
        """Response must include task_detection with needs_rag and needs_agent."""
        response = test_client.post(
            "/invoke", json={"app_id": "mock_app", "user_input": "Test"}
        )
        data = response.json()
        assert "task_detection" in data
        assert "needs_rag" in data["task_detection"]
        assert "needs_agent" in data["task_detection"]
