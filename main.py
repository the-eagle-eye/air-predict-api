"""
FastAPI application for CR310 datalogger data reception.
"""
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from datetime import datetime
from typing import Dict, Optional
import os
from dotenv import load_dotenv

from models import CR310Reading, APIResponse, ReadingsListResponse
from database import MongoDBClient
from validator import ReadingValidator
from preprocessor import DataPreprocessor

load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CR310 Datalogger API",
    description="API for receiving and storing CR310 datalogger readings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response time middleware
class ResponseTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(ResponseTimeMiddleware)


# Initialize MongoDB client
try:
    db_client = MongoDBClient()
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    db_client = None


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if db_client:
        db_client.close()


@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint - health check"""
    return APIResponse(
        success=True,
        message="CR310 Datalogger API is running",
        code=200,
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    if db_client is None:
        return APIResponse(
            success=False,
            message="Database connection failed",
            code=500,
            timestamp=datetime.utcnow()
        )
    
    try:
        # Test database connection
        db_client.client.server_info()
        return APIResponse(
            success=True,
            message="Service is healthy",
            code=200,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            success=False,
            message=f"Database connection error: {str(e)}",
            code=500,
            timestamp=datetime.utcnow()
        )


@app.post("/api/v1/readings", response_model=APIResponse, status_code=status.HTTP_200_OK)
async def receive_reading(data: Dict):
    """
    Receive and store CR310 datalogger reading
    
    This endpoint:
    - Validates JSON structure and required fields (US2)
    - Checks for duplicates and invalid ranges (US2)
    - Preprocesses and normalizes data (US4)
    - Stores in MongoDB (US4)
    - Returns appropriate HTTP status codes (US3)
    - Ensures response time < 1 second (US3)
    """
    start_time = time.time()
    
    try:
        # Check database connection
        if db_client is None:
            logger.error("Database client not initialized")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection unavailable"
            )
        
        # Validate reading (US2: JSON structure, required fields, ranges)
        is_valid, error_message = ReadingValidator.validate_reading(
            data,
            check_duplicate=lambda equipo, timestamp: db_client.is_duplicate(equipo, timestamp)
        )
        
        if not is_valid:
            logger.warning(f"Validation failed: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Preprocess and clean data (US4)
        cleaned_data = DataPreprocessor.clean_reading(data)
        
        if cleaned_data is None:
            logger.warning("Data cleaning failed - inconsistent or null values")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data cleaning failed: null or inconsistent values detected"
            )
        
        # Check for inconsistent values (US4)
        if not DataPreprocessor.remove_inconsistent_values(cleaned_data):
            logger.warning("Inconsistent values detected")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inconsistent values detected in reading"
            )
        
        # Store in MongoDB (US4)
        success = db_client.insert_reading(cleaned_data)
        
        if not success:
            # Duplicate detected (insert_reading returns False for duplicates)
            logger.warning(f"Duplicate reading: {data.get('equipo')} - {data.get('timestamp')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate reading detected"
            )
        
        # Check response time (US3)
        process_time = time.time() - start_time
        if process_time > 1.0:
            logger.warning(f"Response time exceeded 1 second: {process_time:.3f}s")
        
        logger.info(f"Reading stored successfully: {cleaned_data['equipo']} - {cleaned_data['timestamp']}")
        
        # Return success response (US3: HTTP 200)
        return APIResponse(
            success=True,
            message="Reading stored successfully",
            code=200,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors (US3: HTTP 500)
        logger.error(f"Unexpected error processing reading: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while processing reading"
        )


@app.get("/api/v1/readings", response_model=ReadingsListResponse)
async def get_readings(
    equipo: Optional[str] = Query(None, description="Filter by equipment ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return (max 1000)"),
    offset: int = Query(0, ge=0, description="Number of records to skip for pagination")
):
    """
    Get CR310 datalogger readings with optional filters
    
    - **equipo**: Filter by specific equipment (e.g., "T101")
    - **start_date**: Get readings from this date onwards
    - **end_date**: Get readings up to this date
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **offset**: Skip this many records (for pagination)
    
    Returns readings sorted by timestamp (most recent first)
    """
    try:
        # Check database connection
        if db_client is None:
            logger.error("Database client not initialized")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection unavailable"
            )
        
        # Get readings with filters
        readings, total_count = db_client.get_readings(
            equipo=equipo,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        # Build response message
        filters = []
        if equipo:
            filters.append(f"equipo={equipo}")
        if start_date:
            filters.append(f"from {start_date}")
        if end_date:
            filters.append(f"to {end_date}")
        
        filter_msg = f" with filters: {', '.join(filters)}" if filters else ""
        
        return ReadingsListResponse(
            success=True,
            message=f"Retrieved {len(readings)} of {total_count} readings{filter_msg}",
            count=len(readings),
            total=total_count,
            data=readings,
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Unexpected errors
        logger.error(f"Error retrieving readings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving readings from database"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

