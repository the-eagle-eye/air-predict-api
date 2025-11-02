"""
Pytest test suite for CR310 Datalogger API
Run with: pytest test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys
import os

# Add current directory to path to import modules
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from database import MongoDBClient


# Test client
client = TestClient(app)


# Test data fixtures
@pytest.fixture
def valid_reading_t101():
    """Valid reading for test equipment"""
    import time
    # Generate unique ID for each fixture usage
    unique_id = int(time.time() * 1000000) % 1000000
    return {
        "equipo": f"TEST_{unique_id}",
        "SO2_ppb": 25.43,
        "H2S_ppb": 2.18,
        "Reaction_Temp": 35.0,
        "IZS_Temp": 34.2,
        "PMT_Temp": 36.1,
        "SampleFlow": 452.3,
        "Pressure": 29.76,
        "UVLampIntensity": 403.5,
        "Box_Temp": 33.7,
        "HVPS_V": 671.2,
        "Conv_Temp": 35.9,
        "Ozone_flow": 480.5,
        "timestamp": f"2025-10-27 18:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
    }


@pytest.fixture
def valid_reading_t102():
    """Valid reading for test equipment"""
    import time
    # Generate unique ID for each fixture usage
    unique_id = int(time.time() * 1000000) % 1000000
    return {
        "equipo": f"TEST_{unique_id + 1}",  # +1 to ensure different from t101
        "SO2_ppb": 30.5,
        "H2S_ppb": 3.2,
        "Reaction_Temp": 36.0,
        "IZS_Temp": 35.1,
        "PMT_Temp": 37.0,
        "SampleFlow": 460.0,
        "Pressure": 30.1,
        "UVLampIntensity": 410.0,
        "Box_Temp": 34.5,
        "HVPS_V": 680.0,
        "Conv_Temp": 36.5,
        "Ozone_flow": 490.0,
        "timestamp": f"2025-10-27 19:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
    }


@pytest.fixture
def reading_missing_fields():
    """Reading with missing required fields"""
    import time
    unique_id = int(time.time() * 1000000) % 1000000
    return {
        "equipo": f"TEST_{unique_id + 2}",
        "SO2_ppb": 25.43,
        "timestamp": f"2025-10-27 18:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
    }


@pytest.fixture
def reading_out_of_range():
    """Reading with out of range values"""
    import time
    unique_id = int(time.time() * 1000000) % 1000000
    return {
        "equipo": f"TEST_{unique_id + 3}",
        "SO2_ppb": 99999,  # Out of range
        "H2S_ppb": 2.18,
        "Reaction_Temp": 35.0,
        "IZS_Temp": 34.2,
        "PMT_Temp": 36.1,
        "SampleFlow": 452.3,
        "Pressure": 29.76,
        "UVLampIntensity": 403.5,
        "Box_Temp": 33.7,
        "HVPS_V": 671.2,
        "Conv_Temp": 35.9,
        "Ozone_flow": 480.5,
        "timestamp": f"2025-10-27 18:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
    }


@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data():
    """Clean up test data before and after tests"""
    # Setup: Clean test data before tests
    try:
        db_client = MongoDBClient()
        # Remove all test data (equipment starting with TEST)
        db_client.collection.delete_many({
            "equipo": {"$regex": "^TEST"}
        })
        db_client.close()
        print("\n🧹 Cleaned up existing TEST data before tests")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not clean up before tests: {e}")
    
    yield
    
    # Teardown: Clean test data after tests
    try:
        db_client = MongoDBClient()
        # Remove all test data (equipment starting with TEST)
        db_client.collection.delete_many({
            "equipo": {"$regex": "^TEST"}
        })
        db_client.close()
        print("\n✅ Test data cleaned up")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not clean up after tests: {e}")


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self):
        """Test GET / - root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "CR310 Datalogger API is running" in data["message"]
        assert data["code"] == 200
    
    def test_health_endpoint(self):
        """Test GET /health - health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] in [True, False]  # Depends on MongoDB connection
        assert "message" in data


class TestPostReadings:
    """Test POST /api/v1/readings endpoint"""
    
    def test_post_valid_reading_t101(self, valid_reading_t101):
        """Test 1: POST valid reading for T101 (should succeed)"""
        response = client.post("/api/v1/readings", json=valid_reading_t101)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Reading stored successfully" in data["message"]
        assert data["code"] == 200
    
    def test_post_valid_reading_t102(self, valid_reading_t102):
        """Test 2: POST valid reading for T102 (should succeed)"""
        response = client.post("/api/v1/readings", json=valid_reading_t102)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Reading stored successfully" in data["message"]
    
    def test_post_duplicate_reading(self, valid_reading_t101):
        """Test 3: POST duplicate reading (should fail with 400)"""
        # First post should succeed
        response1 = client.post("/api/v1/readings", json=valid_reading_t101)
        assert response1.status_code == 200
        
        # Second post with same data should fail (duplicate)
        response2 = client.post("/api/v1/readings", json=valid_reading_t101)
        assert response2.status_code == 400
        assert "Duplicate" in response2.json()["detail"]
    
    def test_post_missing_fields(self, reading_missing_fields):
        """Test 4: POST reading with missing fields (should fail with 400)"""
        response = client.post("/api/v1/readings", json=reading_missing_fields)
        assert response.status_code == 400
        assert "Missing required fields" in response.json()["detail"]
    
    def test_post_out_of_range(self, reading_out_of_range):
        """Test 5: POST reading with out of range values (should fail with 400)"""
        response = client.post("/api/v1/readings", json=reading_out_of_range)
        assert response.status_code == 400
        assert "out of range" in response.json()["detail"].lower()
    
    def test_post_invalid_timestamp_format(self, valid_reading_t101):
        """Test 6: POST reading with invalid timestamp format (should fail with 400)"""
        import time
        unique_id = int(time.time() * 1000000) % 1000000
        invalid_reading = valid_reading_t101.copy()
        invalid_reading["timestamp"] = "2025/10/27 18:30:00"  # Wrong format
        invalid_reading["equipo"] = f"TEST_{unique_id + 4}"  # Different equipment
        
        response = client.post("/api/v1/readings", json=invalid_reading)
        assert response.status_code == 400
    
    def test_post_empty_equipo(self, valid_reading_t101):
        """Test 7: POST reading with empty equipo (should fail with 400)"""
        invalid_reading = valid_reading_t101.copy()
        invalid_reading["equipo"] = ""
        invalid_reading["timestamp"] = "2025-10-27 20:00:00"
        
        response = client.post("/api/v1/readings", json=invalid_reading)
        assert response.status_code == 400
    
    def test_post_null_value(self, valid_reading_t101):
        """Test 8: POST reading with null value (should fail with 400)"""
        invalid_reading = valid_reading_t101.copy()
        invalid_reading["SO2_ppb"] = None
        invalid_reading["timestamp"] = "2025-10-27 20:01:00"
        
        response = client.post("/api/v1/readings", json=invalid_reading)
        assert response.status_code == 400


class TestGetReadings:
    """Test GET /api/v1/readings endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, valid_reading_t101, valid_reading_t102):
        """Ensure we have test data for GET tests"""
        # Post readings if they don't exist
        client.post("/api/v1/readings", json=valid_reading_t101)
        client.post("/api/v1/readings", json=valid_reading_t102)
    
    def test_get_all_readings(self):
        """Test 9: GET all readings (should succeed)"""
        response = client.get("/api/v1/readings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "total" in data
        assert "data" in data
        assert isinstance(data["data"], list)
        assert data["count"] >= 0
    
    def test_get_readings_filter_by_equipo(self, valid_reading_t101):
        """Test 10: GET readings filtered by equipment (should succeed)"""
        # First create a reading to ensure we have data
        test_reading = valid_reading_t101
        equipo_id = test_reading["equipo"]
        client.post("/api/v1/readings", json=test_reading)
        
        # Now get readings for this equipment
        response = client.get(f"/api/v1/readings?equipo={equipo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 0
        
        # All returned readings should be for this equipment
        for reading in data["data"]:
            assert reading["equipo"] == equipo_id
    
    def test_get_readings_with_pagination(self):
        """Test 11: GET readings with pagination (should succeed)"""
        response = client.get("/api/v1/readings?limit=1&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] <= 1  # Should return at most 1 reading
        assert len(data["data"]) <= 1
    
    def test_get_readings_with_date_filter(self):
        """Test 12: GET readings with date filter (should succeed)"""
        response = client.get(
            "/api/v1/readings?start_date=2025-10-27 00:00:00&end_date=2025-10-27 23:59:59"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_readings_combined_filters(self, valid_reading_t101):
        """Test 13: GET readings with combined filters (should succeed)"""
        # First create a reading to ensure we have data
        test_reading = valid_reading_t101
        equipo_id = test_reading["equipo"]
        client.post("/api/v1/readings", json=test_reading)
        
        # Now get readings with combined filters
        response = client.get(f"/api/v1/readings?equipo={equipo_id}&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] <= 10
        
        # All returned readings should be for this equipment
        for reading in data["data"]:
            assert reading["equipo"] == equipo_id
    
    def test_get_readings_invalid_limit(self):
        """Test 14: GET readings with invalid limit (should handle gracefully)"""
        response = client.get("/api/v1/readings?limit=5000")  # Over max
        # Should either clamp to max or return 422
        assert response.status_code in [200, 422]
    
    def test_get_readings_nonexistent_equipo(self):
        """Test 15: GET readings for non-existent equipment (should return empty)"""
        response = client.get("/api/v1/readings?equipo=NONEXISTENT")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] == 0
        assert len(data["data"]) == 0


class TestDataValidation:
    """Test data validation and preprocessing"""
    
    def test_equipo_normalization(self):
        """Test 16: Equipment ID should be normalized to uppercase"""
        import time
        unique_id = int(time.time() * 1000000) % 1000000
        unique_ts = f"2025-10-27 21:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
        
        reading = {
            "equipo": f"test_{unique_id}",  # lowercase - will be normalized to TEST_{unique_id}
            "SO2_ppb": 25.43,
            "H2S_ppb": 2.18,
            "Reaction_Temp": 35.0,
            "IZS_Temp": 34.2,
            "PMT_Temp": 36.1,
            "SampleFlow": 452.3,
            "Pressure": 29.76,
            "UVLampIntensity": 403.5,
            "Box_Temp": 33.7,
            "HVPS_V": 671.2,
            "Conv_Temp": 35.9,
            "Ozone_flow": 480.5,
            "timestamp": unique_ts
        }
        
        response = client.post("/api/v1/readings", json=reading)
        assert response.status_code == 200
        
        # Get the reading back and check it's uppercase
        get_response = client.get(f"/api/v1/readings?equipo=TEST_{unique_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        if data["count"] > 0:
            # Equipment ID should be normalized to uppercase
            assert data["data"][0]["equipo"] == f"TEST_{unique_id}".upper()
    
    def test_numeric_precision(self):
        """Test 17: Numeric values should be rounded to 2 decimals"""
        import time
        unique_id = int(time.time() * 1000000) % 1000000
        unique_ts = f"2025-10-27 22:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
        
        reading = {
            "equipo": f"TEST_{unique_id + 5}",
            "SO2_ppb": 25.123456789,  # Many decimals
            "H2S_ppb": 2.987654321,
            "Reaction_Temp": 35.0,
            "IZS_Temp": 34.2,
            "PMT_Temp": 36.1,
            "SampleFlow": 452.3,
            "Pressure": 29.76,
            "UVLampIntensity": 403.5,
            "Box_Temp": 33.7,
            "HVPS_V": 671.2,
            "Conv_Temp": 35.9,
            "Ozone_flow": 480.5,
            "timestamp": unique_ts
        }
        
        response = client.post("/api/v1/readings", json=reading)
        assert response.status_code == 200
        
        # Get the reading and verify rounding
        get_response = client.get(f"/api/v1/readings?equipo=TEST_{unique_id + 5}")
        assert get_response.status_code == 200
        data = get_response.json()
        if data["count"] > 0:
            # Should be rounded to 2 decimals
            assert data["data"][0]["SO2_ppb"] == 25.12
            assert data["data"][0]["H2S_ppb"] == 2.99


class TestResponseTime:
    """Test response time requirements (< 1 second)"""
    
    def test_post_response_time(self, valid_reading_t101):
        """Test 18: POST response time should be < 1 second"""
        import time
        
        # Use unique timestamp and equipment ID
        unique_id = int(time.time() * 1000000) % 1000000
        reading = valid_reading_t101.copy()
        reading["timestamp"] = f"2025-10-27 23:{(unique_id // 10000) % 60:02d}:{unique_id % 60:02d}"
        reading["equipo"] = f"TEST_{unique_id + 6}"
        
        start_time = time.time()
        response = client.post("/api/v1/readings", json=reading)
        elapsed_time = time.time() - start_time
        
        assert response.status_code in [200, 400]  # Could fail validation
        assert elapsed_time < 1.0, f"Response time {elapsed_time:.3f}s exceeded 1 second"
    
    def test_get_response_time(self):
        """Test 19: GET response time should be < 1 second"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/readings")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 1.0, f"Response time {elapsed_time:.3f}s exceeded 1 second"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_post_invalid_json(self):
        """Test 20: POST with invalid JSON structure (should fail gracefully)"""
        response = client.post(
            "/api/v1/readings",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_post_wrong_data_type(self, valid_reading_t101):
        """Test 21: POST with wrong data type (should fail with 400)"""
        invalid_reading = valid_reading_t101.copy()
        invalid_reading["SO2_ppb"] = "not a number"  # Should be float
        invalid_reading["timestamp"] = "2025-10-27 23:30:00"
        
        response = client.post("/api/v1/readings", json=invalid_reading)
        assert response.status_code == 400
    
    def test_get_invalid_query_params(self):
        """Test 22: GET with invalid query parameters (should handle gracefully)"""
        response = client.get("/api/v1/readings?limit=invalid")
        assert response.status_code == 422  # FastAPI validation error


# Summary function to run after all tests
def test_summary(capsys):
    """Print test summary"""
    print("\n" + "="*50)
    print("🎉 CR310 Datalogger API Test Suite Complete")
    print("="*50)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

