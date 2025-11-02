#!/bin/bash

# Test script for CR310 Datalogger API

API_URL="http://localhost:8000"

echo "🧪 Testing CR310 Datalogger API"
echo "================================"
echo ""

# Test 1: Health check
echo "1️⃣  Testing health check..."
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Send valid reading
echo "2️⃣  Testing valid reading submission..."
curl -s -X POST "$API_URL/api/v1/readings" \
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
  }' | python3 -m json.tool
echo ""
echo ""

# Test 3: Send duplicate reading (should fail)
echo "3️⃣  Testing duplicate reading (should fail with 400)..."
curl -s -X POST "$API_URL/api/v1/readings" \
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
echo ""
echo ""

# Test 4: Send reading with missing field (should fail)
echo "4️⃣  Testing missing field (should fail with 400)..."
curl -s -X POST "$API_URL/api/v1/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "equipo": "T101",
    "SO2_ppb": 25.43,
    "timestamp": "2025-10-27 18:31:00"
  }'
echo ""
echo ""

# Test 5: Send reading with out of range value (should fail)
echo "5️⃣  Testing out of range value (should fail with 400)..."
curl -s -X POST "$API_URL/api/v1/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "equipo": "T102",
    "SO2_ppb": 99999,
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
    "timestamp": "2025-10-27 18:32:00"
  }'
echo ""
echo ""

# Test 6: Send a valid reading with different timestamp
echo "6️⃣  Testing another valid reading (for GET tests)..."
curl -s -X POST "$API_URL/api/v1/readings" \
  -H "Content-Type: application/json" \
  -d '{
    "equipo": "T102",
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
    "timestamp": "2025-10-27 19:00:00"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 7: GET all readings
echo "7️⃣  Testing GET all readings..."
curl -s "$API_URL/api/v1/readings" | python3 -m json.tool
echo ""
echo ""

# Test 8: GET readings filtered by equipment
echo "8️⃣  Testing GET readings filtered by equipo=T101..."
curl -s "$API_URL/api/v1/readings?equipo=T101" | python3 -m json.tool
echo ""
echo ""

# Test 9: GET with pagination
echo "9️⃣  Testing GET with pagination (limit=1)..."
curl -s "$API_URL/api/v1/readings?limit=1" | python3 -m json.tool
echo ""
echo ""

echo "✅ Testing complete!"

