# 🚀 Quick Start Guide - CR310 Datalogger API

## ⚡ Fast Setup (3 steps)

### 1. Activate Virtual Environment
```bash
source bin/activate
```

### 2. Start MongoDB
```bash
# macOS with Homebrew
brew services start mongodb-community

# OR using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. Run the API
```bash
./start.sh
# OR
python main.py
```

✅ **Done!** Your API is now running at: http://localhost:8000

---

## 📝 Quick Test

In another terminal:

```bash
# Run automated test suite (recommended)
./run_tests.sh

# OR manually test with curl
curl -X POST "http://localhost:8000/api/v1/readings" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## 📚 Important URLs

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔧 Troubleshooting

### ❌ MongoDB Connection Error
**Problem**: `Database connection unavailable`

**Solution**:
```bash
# Check if MongoDB is running
mongosh --eval "db.version()"

# If not, start it:
brew services start mongodb-community  # macOS
# OR
sudo systemctl start mongod  # Linux
# OR
docker run -d -p 27017:27017 --name mongodb mongo:latest  # Docker
```

### ❌ Port Already in Use
**Problem**: `Address already in use: 8000`

**Solution**: Change port in `.env` file:
```env
API_PORT=8001
```

### ❌ Import Errors
**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
source bin/activate  # Activate venv first!
pip install -r requirements.txt
```

---

## 📊 User Stories Completed

✅ **US1**: Datalogger sends data via POST API
✅ **US2**: Data validation (JSON structure, required fields, duplicates, ranges)
✅ **US3**: HTTP response codes (200, 400, 500) with < 1s response time
✅ **US4**: MongoDB storage with automatic data preprocessing

---

## 📂 Project Files

```
datalogger-v1/
├── main.py              # FastAPI application
├── models.py            # Data validation models
├── database.py          # MongoDB client
├── validator.py         # Business logic validation
├── preprocessor.py      # Data cleaning
├── requirements.txt     # Dependencies
├── .env                 # Configuration
├── start.sh            # Quick start script
├── test_request.sh     # Test script
├── README.md           # Full documentation
└── QUICKSTART.md       # This file
```

---

## 🎯 Next Steps

1. Configure your CR310 datalogger to send POST requests to:
   `http://your-server:8000/api/v1/readings`

2. Monitor logs for incoming data

3. Query MongoDB to see stored readings:
   ```bash
   mongosh
   use datalogger_db
   db.cr310_readings.find().pretty()
   ```

4. For production: Update CORS settings in `main.py`

---

## 💡 Tips

- All numeric values are automatically rounded to 2 decimals
- Equipment IDs are normalized to uppercase
- Duplicate readings (same equipo + timestamp) are rejected
- Out-of-range values are rejected automatically
- MongoDB connection is tested on startup

---

Need more details? Check **README.md** for full documentation!

