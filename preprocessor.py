"""
Data preprocessing, cleaning and normalization for CR310 readings
"""
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocesses and normalizes CR310 readings"""
    
    @staticmethod
    def clean_reading(data: Dict) -> Optional[Dict]:
        """
        Clean and normalize a reading
        Returns cleaned dict or None if invalid
        """
        try:
            cleaned = {}
            
            # Normalize equipo
            cleaned['equipo'] = data['equipo'].strip().upper()
            
            # Convert timestamp to datetime object for storage
            timestamp_str = data['timestamp']
            try:
                timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                cleaned['timestamp'] = timestamp_str  # Keep original format
                cleaned['timestamp_dt'] = timestamp_dt  # Also store as datetime
            except ValueError:
                logger.error(f"Invalid timestamp format: {timestamp_str}")
                return None
            
            # Normalize all numeric fields
            numeric_fields = [
                'SO2_ppb', 'H2S_ppb', 'Reaction_Temp', 'IZS_Temp',
                'PMT_Temp', 'SampleFlow', 'Pressure', 'UVLampIntensity',
                'Box_Temp', 'HVPS_V', 'Conv_Temp', 'Ozone_flow'
            ]
            
            for field in numeric_fields:
                value = data.get(field)
                
                # Remove null or None values
                if value is None:
                    logger.warning(f"Null value detected for {field}, skipping reading")
                    return None
                
                # Convert to float and round to 2 decimals
                try:
                    cleaned[field] = round(float(value), 2)
                except (ValueError, TypeError):
                    logger.error(f"Invalid numeric value for {field}: {value}")
                    return None
            
            # Add metadata
            cleaned['created_at'] = datetime.utcnow()
            cleaned['source'] = 'CR310'
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning reading: {e}")
            return None
    
    @staticmethod
    def remove_inconsistent_values(data: Dict) -> bool:
        """
        Check for inconsistent values and remove if found
        Returns True if data is consistent, False otherwise
        """
        # Check for inconsistent temperature readings
        temps = [
            data.get('Reaction_Temp'),
            data.get('IZS_Temp'),
            data.get('PMT_Temp'),
            data.get('Box_Temp'),
            data.get('Conv_Temp')
        ]
        
        # Remove None values
        temps = [t for t in temps if t is not None]
        
        if len(temps) < 2:
            return True  # Not enough data to check consistency
        
        # Check if temperatures are within reasonable range of each other
        temp_range = max(temps) - min(temps)
        if temp_range > 30:  # More than 30°C difference
            logger.warning(f"Large temperature range detected: {temp_range}°C")
            return False
        
        return True

