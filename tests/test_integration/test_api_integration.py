"""Integration tests for API endpoints with mock servers."""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.api.main import app


class TestAPIIntegration:
    """Integration tests for API endpoints."""
    
    def test_complete_etl_workflow(self, client, mock_httpx_client_fixture):
        """Test complete ETL workflow through API."""
        with patch('src.etl.pipeline.httpx.AsyncClient', return_value=mock_httpx_client_fixture):
            # Trigger ETL
            etl_response = client.post("/etl/run")
            assert etl_response.status_code == 200
            
            etl_data = etl_response.json()
            assert etl_data["status"] == "ok"
            assert etl_data["museums"] > 0
            assert etl_data["cities"] > 0
    
    def test_features_endpoint_after_etl(self, client, mock_httpx_client_fixture):
        """Test features endpoint after running ETL."""
        with patch('src.etl.pipeline.httpx.AsyncClient', return_value=mock_httpx_client_fixture):
            # Run ETL first
            etl_response = client.post("/etl/run")
            assert etl_response.status_code == 200
            
            # Get features
            features_response = client.get("/features")
            assert features_response.status_code == 200
            
            features_data = features_response.json()
            assert "columns" in features_data
            assert "rows" in features_data
            assert len(features_data["columns"]) > 0
    
    def test_model_endpoint_after_etl(self, client, mock_httpx_client_fixture):
        """Test model endpoint after running ETL."""
        with patch('src.etl.pipeline.httpx.AsyncClient', return_value=mock_httpx_client_fixture):
            # Run ETL first
            etl_response = client.post("/etl/run")
            assert etl_response.status_code == 200
            
            # Get model results
            model_response = client.get("/model/linear")
            assert model_response.status_code == 200
            
            model_data = model_response.json()
            assert "model" in model_data
            assert "n_samples" in model_data
            assert model_data["n_samples"] > 0
    
    def test_api_error_handling(self, client):
        """Test API error handling with external API failures."""
        # Mock external API failure
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("External API Error")
        
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        
        with patch('src.etl.pipeline.httpx.AsyncClient', return_value=mock_client):
            # Trigger ETL - should handle error gracefully
            etl_response = client.post("/etl/run")
            assert etl_response.status_code == 200  # API should return 200 even if ETL fails
            
            etl_data = etl_response.json()
            assert etl_data["status"] == "error"
            assert "External API Error" in etl_data["error"]
    
    def test_concurrent_requests(self, client, mock_httpx_client_fixture):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('src.etl.pipeline.httpx.AsyncClient', return_value=mock_httpx_client_fixture):
                response = client.post("/etl/run")
                results.append(response.status_code)
        
        # Make 3 concurrent requests
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 3
    
    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI schema
        schema_response = client.get("/openapi.json")
        assert schema_response.status_code == 200
        
        # Test Swagger UI
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        
        # Test ReDoc
        redoc_response = client.get("/redoc")
        assert redoc_response.status_code == 200
