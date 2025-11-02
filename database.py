"""
MongoDB database connection and operations
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class MongoDBClient:
    """Simple MongoDB client for CR310 readings"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
            database_name = os.getenv('MONGODB_DATABASE', 'datalogger_db')
            collection_name = os.getenv('MONGODB_COLLECTION', 'cr310_readings')
            
            self.client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            
            # Create index on equipo and timestamp to prevent duplicates
            self.collection.create_index([("equipo", 1), ("timestamp", 1)], unique=True)
            
            logger.info(f"Connected to MongoDB: {database_name}/{collection_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def insert_reading(self, reading: Dict) -> bool:
        """
        Insert a reading into MongoDB
        Returns True if successful, False if duplicate or error
        """
        try:
            result = self.collection.insert_one(reading)
            logger.info(f"Reading inserted with ID: {result.inserted_id}")
            return True
        except DuplicateKeyError:
            logger.warning(f"Duplicate reading detected: {reading.get('equipo')} - {reading.get('timestamp')}")
            return False
        except Exception as e:
            logger.error(f"Error inserting reading: {e}")
            raise
    
    def is_duplicate(self, equipo: str, timestamp: str) -> bool:
        """Check if a reading with same equipo and timestamp exists"""
        count = self.collection.count_documents({
            "equipo": equipo,
            "timestamp": timestamp
        })
        return count > 0
    
    def get_readings(self, equipo: Optional[str] = None, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None,
                     limit: int = 100, 
                     offset: int = 0) -> tuple:
        """
        Get readings with optional filters and pagination
        Returns (readings_list, total_count)
        """
        try:
            # Build filter query
            query = {}
            
            if equipo:
                query["equipo"] = equipo
            
            if start_date:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$gte"] = start_date
            
            if end_date:
                query["timestamp"] = query.get("timestamp", {})
                query["timestamp"]["$lte"] = end_date
            
            # Get total count
            total_count = self.collection.count_documents(query)
            
            # Get paginated results, sorted by timestamp descending
            readings = list(self.collection.find(query)
                          .sort("timestamp", -1)
                          .skip(offset)
                          .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for reading in readings:
                reading["_id"] = str(reading["_id"])
            
            logger.info(f"Retrieved {len(readings)} readings (total: {total_count})")
            return readings, total_count
            
        except Exception as e:
            logger.error(f"Error retrieving readings: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

