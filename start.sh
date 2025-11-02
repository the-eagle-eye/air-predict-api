#!/bin/bash

# Start script for CR310 Datalogger API

echo "🚀 Starting CR310 Datalogger API..."
echo ""

# Check if MongoDB is running
echo "📊 Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    mongosh --eval "db.version()" --quiet > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ MongoDB is running"
    else
        echo "⚠️  MongoDB is not running. Please start MongoDB first:"
        echo "   - macOS: brew services start mongodb-community"
        echo "   - Linux: sudo systemctl start mongod"
        echo "   - Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest"
        echo ""
    fi
else
    echo "⚠️  MongoDB CLI (mongosh) not found. Make sure MongoDB is installed and running."
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source bin/activate

# Start the server
echo "🌐 Starting FastAPI server..."
echo "📝 API Documentation will be available at: http://localhost:8000/docs"
echo ""

python main.py

