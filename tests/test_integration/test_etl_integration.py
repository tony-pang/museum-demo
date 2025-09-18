"""Integration tests for ETL pipeline with mock servers."""
import pytest
from unittest.mock import patch, AsyncMock
from src.etl.pipeline import run_etl


class TestETLIntegration:
    """Integration tests for ETL pipeline."""
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.httpx.AsyncClient')
    def test_etl_pipeline_with_mock_apis(self, mock_httpx_client, mock_create_all, mock_httpx_client_fixture):
        """Test complete ETL pipeline with mocked external APIs."""
        # Configure the mock client
        mock_httpx_client.return_value = mock_httpx_client_fixture
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Verify the result
        assert result["status"] == "ok"
        assert "museums" in result
        assert "cities" in result
        assert result["museums"] > 0
        assert result["cities"] > 0
        
        # Verify database creation was called
        mock_create_all.assert_called_once()
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.httpx.AsyncClient')
    def test_etl_pipeline_wikipedia_api_failure(self, mock_httpx_client, mock_create_all):
        """Test ETL pipeline when Wikipedia API fails."""
        # Mock Wikipedia API failure
        mock_client = AsyncMock()
        wikipedia_response = AsyncMock()
        wikipedia_response.status_code = 500
        wikipedia_response.raise_for_status.side_effect = Exception("API Error")
        
        mock_client.get.return_value = wikipedia_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_httpx_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Verify error handling
        assert result["status"] == "error"
        assert "error" in result
        assert "API Error" in result["error"]
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.httpx.AsyncClient')
    def test_etl_pipeline_wikidata_api_failure(self, mock_httpx_client, mock_create_all, mock_httpx_client_fixture):
        """Test ETL pipeline when Wikidata API fails."""
        # Configure Wikipedia to succeed but Wikidata to fail
        mock_client = AsyncMock()
        
        # Wikipedia response (success)
        wikipedia_response = AsyncMock()
        wikipedia_response.status_code = 200
        wikipedia_response.json.return_value = {
            "parse": {
                "text": {
                    "*": """
                    <table class="wikitable sortable">
                    <tr><th>Museum</th><th>City</th><th>Visitors</th></tr>
                    <tr><td>Louvre</td><td>Paris</td><td>9,600,000 (2023)</td></tr>
                    </table>
                    """
                }
            }
        }
        
        # Wikidata response (failure)
        wikidata_response = AsyncMock()
        wikidata_response.status_code = 500
        wikidata_response.raise_for_status.side_effect = Exception("Wikidata API Error")
        
        # Configure mock client to return different responses based on URL
        async def mock_get(url, **kwargs):
            if "wikipedia.org" in url:
                return wikipedia_response
            elif "wikidata.org" in url:
                return wikidata_response
            else:
                raise ValueError(f"Unexpected URL: {url}")
        
        mock_client.get = mock_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_httpx_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Should still succeed but with no population data
        assert result["status"] == "ok"
        assert result["museums"] > 0
        assert result["cities"] == 0  # No cities due to Wikidata failure
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.httpx.AsyncClient')
    def test_etl_pipeline_timeout_handling(self, mock_httpx_client, mock_create_all):
        """Test ETL pipeline timeout handling."""
        # Mock timeout
        mock_client = AsyncMock()
        mock_client.get.side_effect = asyncio.TimeoutError("Request timeout")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_httpx_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Verify error handling
        assert result["status"] == "error"
        assert "timeout" in result["error"].lower()
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.httpx.AsyncClient')
    def test_etl_pipeline_malformed_data(self, mock_httpx_client, mock_create_all):
        """Test ETL pipeline with malformed data."""
        # Mock malformed Wikipedia response
        mock_client = AsyncMock()
        wikipedia_response = AsyncMock()
        wikipedia_response.status_code = 200
        wikipedia_response.json.return_value = {
            "parse": {
                "text": {
                    "*": "<p>No table found</p>"  # No museum data
                }
            }
        }
        
        mock_client.get.return_value = wikipedia_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_httpx_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Should handle gracefully
        assert result["status"] == "ok"
        assert result["museums"] == 0
        assert result["cities"] == 0
