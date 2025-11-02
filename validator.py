"""
Business logic validation for CR310 readings
"""
from typing import Dict, Tuple, Optional
from models import CR310Reading
import logging

logger = logging.getLogger(__name__)


class ReadingValidator:
    """Validates CR310 readings according to business rules"""
    
    # Valid ranges for each parameter
    VALID_RANGES = {
        'SO2_ppb': (0, 10000),
        'H2S_ppb': (0, 1000),
        'Reaction_Temp': (20, 60),
        'IZS_Temp': (20, 60),
        'PMT_Temp': (20, 60),
        'SampleFlow': (0, 1000),
        'Pressure': (0, 100),
        'UVLampIntensity': (0, 1000),
        'Box_Temp': (20, 60),
        'HVPS_V': (0, 1000),
        'Conv_Temp': (20, 60),
        'Ozone_flow': (0, 1000)
    }
    
    @staticmethod
    def validate_required_fields(data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check if all required fields are present
        Returns (is_valid, error_message)
        """
        required_fields = [
            'equipo', 'SO2_ppb', 'H2S_ppb', 'Reaction_Temp', 'IZS_Temp',
            'PMT_Temp', 'SampleFlow', 'Pressure', 'UVLampIntensity',
            'Box_Temp', 'HVPS_V', 'Conv_Temp', 'Ozone_flow', 'timestamp'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    @staticmethod
    def validate_json_structure(data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate JSON structure matches expected format
        Returns (is_valid, error_message)
        """
        # Check for unexpected fields (optional - can be removed for flexibility)
        expected_fields = set(ReadingValidator.VALID_RANGES.keys()) | {'equipo', 'timestamp'}
        
        unexpected_fields = set(data.keys()) - expected_fields
        if unexpected_fields:
            logger.warning(f"Unexpected fields in data: {unexpected_fields}")
            # Don't fail on this, just log
        
        # Validate data types
        numeric_fields = [k for k, v in ReadingValidator.VALID_RANGES.items()]
        
        for field in numeric_fields:
            if field in data:
                if not isinstance(data[field], (int, float)):
                    return False, f"Field '{field}' must be numeric"
        
        if 'equipo' in data and not isinstance(data['equipo'], str):
            return False, "Field 'equipo' must be a string"
        
        if 'timestamp' in data and not isinstance(data['timestamp'], str):
            return False, "Field 'timestamp' must be a string"
        
        return True, None
    
    @staticmethod
    def validate_ranges(reading: CR310Reading) -> Tuple[bool, Optional[str]]:
        """
        Validate that all values are within acceptable ranges
        Returns (is_valid, error_message)
        """
        out_of_range = []
        
        for field, (min_val, max_val) in ReadingValidator.VALID_RANGES.items():
            value = getattr(reading, field)
            if value < min_val or value > max_val:
                out_of_range.append(f"{field}={value} (valid: {min_val}-{max_val})")
        
        if out_of_range:
            return False, f"Values out of range: {', '.join(out_of_range)}"
        
        return True, None
    
    @staticmethod
    def validate_reading(data: Dict, check_duplicate: callable = None) -> Tuple[bool, Optional[str]]:
        """
        Complete validation of a reading
        Returns (is_valid, error_message)
        """
        # Check required fields
        is_valid, error = ReadingValidator.validate_required_fields(data)
        if not is_valid:
            return False, error
        
        # Check JSON structure
        is_valid, error = ReadingValidator.validate_json_structure(data)
        if not is_valid:
            return False, error
        
        # Validate using Pydantic model
        try:
            reading = CR310Reading(**data)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        
        # Check value ranges
        is_valid, error = ReadingValidator.validate_ranges(reading)
        if not is_valid:
            return False, error
        
        # Check for duplicates (if duplicate checker provided)
        if check_duplicate:
            if check_duplicate(data.get('equipo'), data.get('timestamp')):
                return False, "Duplicate reading detected"
        
        return True, None

