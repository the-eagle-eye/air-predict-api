#!/bin/bash

# Run pytest tests for CR310 Datalogger API

echo "🧪 Running CR310 Datalogger API Test Suite"
echo "==========================================="
echo ""

# Activate virtual environment
source bin/activate

# Check if MongoDB is running
echo "📊 Checking MongoDB connection..."
if command -v mongosh &> /dev/null; then
    mongosh --eval "db.version()" --quiet > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ MongoDB is running"
    else
        echo "⚠️  MongoDB is not running. Some tests may fail."
        echo "   Start MongoDB with: brew services start mongodb-community"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⚠️  MongoDB CLI (mongosh) not found. Tests may fail without MongoDB."
    echo ""
fi

# Run tests based on arguments
if [ "$1" == "coverage" ]; then
    echo "🔍 Running tests with coverage..."
    pytest test_api.py -v --cov=. --cov-report=html --cov-report=term-missing
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
elif [ "$1" == "fast" ]; then
    echo "⚡ Running tests (fast mode)..."
    pytest test_api.py -v --tb=line
elif [ "$1" == "verbose" ]; then
    echo "📝 Running tests (verbose mode)..."
    pytest test_api.py -vv --tb=long
elif [ "$1" == "specific" ] && [ -n "$2" ]; then
    echo "🎯 Running specific test: $2"
    pytest test_api.py -v -k "$2"
else
    echo "▶️  Running all tests..."
    pytest test_api.py -v
fi

echo ""
echo "✅ Test run complete!"

