#!/bin/bash

# Verification script for CR310 Datalogger API setup

echo "🔍 Verifying CR310 Datalogger API Setup"
echo "========================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
if [ $? -eq 0 ]; then
    echo "   ✅ Python installed"
else
    echo "   ❌ Python not found"
fi
echo ""

# Check virtual environment
echo "2️⃣  Checking virtual environment..."
if [ -f "bin/activate" ]; then
    echo "   ✅ Virtual environment found"
else
    echo "   ❌ Virtual environment not found"
fi
echo ""

# Check dependencies
echo "3️⃣  Checking Python dependencies..."
source bin/activate
python -c "import fastapi, uvicorn, pydantic, pymongo, motor, dotenv" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ All dependencies installed"
else
    echo "   ⚠️  Some dependencies missing, run: pip install -r requirements.txt"
fi
echo ""

# Check MongoDB
echo "4️⃣  Checking MongoDB..."
if command -v mongosh &> /dev/null; then
    mongosh --eval "db.version()" --quiet > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ MongoDB is running"
        echo "   📊 MongoDB version: $(mongosh --eval "db.version()" --quiet)"
    else
        echo "   ⚠️  MongoDB not running"
        echo "      Start with: brew services start mongodb-community"
    fi
else
    echo "   ⚠️  MongoDB CLI (mongosh) not found"
    echo "      Install MongoDB or use Docker"
fi
echo ""

# Check configuration files
echo "5️⃣  Checking configuration files..."
if [ -f ".env" ]; then
    echo "   ✅ .env file found"
else
    echo "   ⚠️  .env file not found, creating from example..."
    cp .env.example .env 2>/dev/null || echo "      Create .env manually"
fi
echo ""

# Check project files
echo "6️⃣  Checking project files..."
files=("main.py" "models.py" "database.py" "validator.py" "preprocessor.py" "requirements.txt")
all_present=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
        all_present=false
    fi
done
echo ""

# Summary
echo "📋 Setup Summary"
echo "================"
if $all_present; then
    echo "✅ All project files present"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Make sure MongoDB is running"
    echo "   2. Run: ./start.sh"
    echo "   3. Visit: http://localhost:8000/docs"
    echo ""
else
    echo "⚠️  Some files are missing"
fi

deactivate 2>/dev/null

