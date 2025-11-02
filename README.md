<<<<<<< HEAD
# air-predict-api# air-predict-api
=======
# 🌬️ CR310 Datalogger API

API REST para recibir y almacenar datos del datalogger IoT modelo CR310 con validación completa y almacenamiento en MongoDB.

## 🚀 Quick Start

```bash
# Activate virtual environment
source bin/activate  # Ya incluido en el repositorio

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB connection

# Start MongoDB (if local)
brew services start mongodb-community
# OR with Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Run the API
python main.py
```

**API running at:** http://localhost:8000  
**Documentation:** http://localhost:8000/docs

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Fast setup guide (3 steps)
- **[TESTING.md](TESTING.md)** - Complete testing guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation details
- **[PYTEST_MIGRATION.md](PYTEST_MIGRATION.md)** - Testing migration notes

---

## ✅ Features

- ✅ **POST API** for CR310 datalogger readings
- ✅ **Complete data validation** (JSON structure, required fields, ranges)
- ✅ **Duplicate detection** (equipo + timestamp)
- ✅ **MongoDB storage** with automatic preprocessing
- ✅ **Data normalization** (uppercase IDs, rounded decimals)
- ✅ **HTTP responses** (200, 400, 500) with < 1s response time
- ✅ **25 comprehensive tests** with pytest
- ✅ **Coverage reporting** included
- ✅ **Production ready** with error handling

---

## 🔗 API Endpoints

### POST /api/v1/readings
Receive and store CR310 datalogger readings.

**Request:**
```json
{
  "equipo": "T101",
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
  "timestamp": "2025-10-27 18:30:00"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Reading stored successfully",
  "code": 200,
  "timestamp": "2025-10-27T18:30:00.123456"
}
```

### GET /api/v1/readings
Retrieve stored readings with filters.

**Query Parameters:**
- `equipo` - Filter by equipment ID
- `start_date` - Start date (YYYY-MM-DD HH:MM:SS)
- `end_date` - End date (YYYY-MM-DD HH:MM:SS)
- `limit` - Records to return (default: 100, max: 1000)
- `offset` - Records to skip (pagination)

---

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Run with coverage
./run_tests.sh coverage

# Run specific test
pytest test_api.py::TestPostReadings -v
```

**Test Suite:** 25 tests covering all user stories
- ✅ Health endpoints (2 tests)
- ✅ POST validation (8 tests)
- ✅ GET functionality (7 tests)
- ✅ Data preprocessing (2 tests)
- ✅ Response time (2 tests)
- ✅ Error handling (3 tests)

---

## 📖 User Stories Implemented

### ✅ US1: IoT Data Reception
POST endpoint that receives CR310 datalogger data every 30 minutes.

### ✅ US2: Data Validation
- JSON structure verification
- All 14 required fields validated
- Duplicate detection (equipo + timestamp)
- Valid range checks for all parameters

### ✅ US3: HTTP Response Confirmation
- HTTP 200 for successful operations
- HTTP 400 for validation errors
- HTTP 500 for server errors
- Response time < 1 second (monitored)

### ✅ US4: Data Preprocessing & Storage
- MongoDB storage (migration-ready for DynamoDB)
- Automatic data normalization
- Null/inconsistent value removal
- Equipment ID uppercase normalization
- Numeric precision (2 decimals)

---

## 📊 Project Structure

```
datalogger-v1/
├── main.py                  # FastAPI application
├── models.py                # Pydantic validation models
├── database.py              # MongoDB client
├── validator.py             # Business logic validation
├── preprocessor.py          # Data cleaning & normalization
├── test_api.py              # 25 comprehensive tests
├── requirements.txt         # Python dependencies
├── pytest.ini               # Pytest configuration
├── conftest.py              # Shared test fixtures
├── run_tests.sh             # Test runner script
├── start.sh                 # Quick start script
├── verify_setup.sh          # Setup verification
├── README.md                # This file
├── QUICKSTART.md            # Quick start guide
├── TESTING.md               # Testing documentation
├── PROJECT_SUMMARY.md       # Implementation details
└── PYTEST_MIGRATION.md      # Test migration notes
```

---

## 🛠️ Technologies

- **FastAPI** - High-performance web framework
- **Pydantic** - Data validation
- **MongoDB** - Document database
- **Pytest** - Testing framework
- **Python 3.9+** - Programming language

---

## 🔄 Future: DynamoDB Migration

The architecture is designed for easy migration to DynamoDB:
1. Replace `database.py` with DynamoDB client
2. Adapt data types for DynamoDB
3. Keep validation and preprocessing unchanged

---

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
mongosh --eval "db.version()"

# Start MongoDB
brew services start mongodb-community  # macOS
sudo systemctl start mongod             # Linux
docker run -d -p 27017:27017 mongo     # Docker
```

### Import Errors
```bash
# Activate virtual environment
source bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📝 Configuration

**Environment Variables** (`.env`):
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=datalogger_db
MONGODB_COLLECTION=cr310_readings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

---

## 📞 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔒 Security Notes

- Configure CORS for production
- Use environment variables for sensitive data
- Enable MongoDB authentication
- Implement rate limiting if needed

---

## 📄 License

This project is part of a data acquisition system for air quality monitoring using CR310 dataloggers.

---

## 🤝 Contributing

This is a production system. For contributions or issues, please contact the development team.

---

**Status:** ✅ Production Ready | 25/25 Tests Passing | Full Documentation

Built with ❤️ for air quality monitoring
>>>>>>> 5720fb8 (Initial commit: CR310 Datalogger API)
