"""Integration tests for ETL pipeline with mock servers."""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.etl.pipeline import run_etl


class TestETLIntegration:
    """Integration tests for ETL pipeline."""
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.SessionLocal')
    @patch('src.clients.wikidata.httpx.AsyncClient')
    @patch('src.clients.wikipedia.httpx.AsyncClient')
    def test_etl_pipeline_with_mock_apis(self, mock_wikipedia_client, mock_wikidata_client, mock_session, mock_create_all, mock_httpx_client):
        """Test complete ETL pipeline with mocked external APIs."""
        # Configure the mock clients
        mock_wikidata_client.return_value = mock_httpx_client
        mock_wikipedia_client.return_value = mock_httpx_client
        
        # Configure mock database session
        from unittest.mock import Mock
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.flush = Mock()
        mock_db.commit = Mock()
        mock_db.rollback = Mock()
        
        # Mock city object with id
        mock_city = Mock()
        mock_city.id = 1
        mock_city.name = "Paris"
        mock_city.country = "France"
        mock_city.population = 11000000
        mock_city.population_year = 2023
        mock_city.wikidata_id = "Q90"
        
        # Mock museum object with id
        mock_museum = Mock()
        mock_museum.id = 1
        mock_museum.name = "Louvre"
        mock_museum.city_id = 1
        
        # Configure query results
        def mock_query(model):
            query_mock = Mock()
            if model.__name__ == "City":
                query_mock.filter.return_value.first.return_value = mock_city
            elif model.__name__ == "Museum":
                query_mock.filter.return_value.first.return_value = None  # New museum
            elif model.__name__ == "MuseumStat":
                query_mock.filter.return_value.first.return_value = None  # New stat
            return query_mock
        
        mock_db.query.side_effect = mock_query
        
        mock_session.return_value.__enter__.return_value = mock_db
        mock_session.return_value.__exit__.return_value = None
        
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
    @patch('src.etl.pipeline.SessionLocal')
    @patch('src.clients.wikipedia.httpx.AsyncClient')
    def test_etl_pipeline_wikipedia_api_failure(self, mock_httpx_client, mock_session, mock_create_all):
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
        assert "No museum data available from Wikidata" in result["error"]
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.SessionLocal')
    @patch('src.clients.wikidata.httpx.AsyncClient')
    @patch('src.etl.pipeline.fetch_most_visited_museums')
    def test_etl_pipeline_wikidata_api_failure(self, mock_wikipedia_fetch, mock_wikidata_client, mock_session, mock_create_all):
        """Test ETL pipeline when Wikidata API fails."""
        # Mock Wikipedia to return museum data
        mock_wikipedia_fetch.return_value = [
            {
                "name": "Louvre",
                "city": "Paris",
                "country": "France",
                "visitors": 9600000,
                "year": 2023,
                "source": "wikipedia_api"
            }
        ]

        # Mock Wikidata to fail
        mock_client = AsyncMock()
        wikidata_response = AsyncMock()
        wikidata_response.status_code = 500
        wikidata_response.raise_for_status.side_effect = Exception("Wikidata API Error")
        mock_client.get.return_value = wikidata_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_wikidata_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Should still succeed but with no population data
        assert result["status"] == "ok"
        assert result["museums"] > 0
        assert result["cities"] > 0
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.SessionLocal')
    @patch('src.clients.wikipedia.httpx.AsyncClient')
    @patch('src.clients.wikidata.httpx.AsyncClient')
    def test_etl_pipeline_timeout_handling(self, mock_wikidata_client, mock_wikipedia_client, mock_session, mock_create_all):
        """Test ETL pipeline timeout handling."""
        # Mock timeout
        mock_client = AsyncMock()
        mock_client.get.side_effect = asyncio.TimeoutError("Request timeout")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_wikipedia_client.return_value = mock_client
        mock_wikidata_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Verify error handling
        assert result["status"] == "error"
        assert "No museum data available from Wikidata" in result["error"]
    
    @patch('src.etl.pipeline.Base.metadata.create_all')
    @patch('src.etl.pipeline.SessionLocal')
    @patch('src.clients.wikipedia.httpx.AsyncClient')
    @patch('src.clients.wikidata.httpx.AsyncClient')
    def test_etl_pipeline_malformed_data(self, mock_wikidata_client, mock_wikipedia_client, mock_session, mock_create_all):
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
        mock_wikipedia_client.return_value = mock_client
        mock_wikidata_client.return_value = mock_client
        
        # Run the ETL pipeline
        result = run_etl()
        
        # Should handle gracefully - no museums found is expected
        assert result["status"] == "error"
        assert "No museum data available from Wikidata" in result["error"]
        assert result["museums"] == 0
        assert result["cities"] == 0
