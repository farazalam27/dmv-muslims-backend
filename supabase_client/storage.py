from supabase_client.auth import supabase
from config import settings
import logging
from typing import Optional, Dict, Any
import os
import uuid

logger = logging.getLogger(__name__)

# Define storage buckets
BUCKETS = {
    "profile_pictures": "profile-pictures",
    "restaurant_images": "restaurant-images",
    "event_images": "event-images",
    "masjid_images": "masjid-images",
}

async def upload_file(
    file_path: str,
    bucket_name: str,
    file_id: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Optional[str]:
    """
    Upload a file to Supabase Storage
    
    Args:
        file_path: Path to the file to upload
        bucket_name: Name of the bucket to upload to
        file_id: Optional ID for the file (defaults to UUID)
        content_type: Optional content type of the file
        
    Returns:
        URL of the uploaded file if successful, None otherwise
    """
    try:
        if bucket_name not in BUCKETS.values():
            logger.error(f"Invalid bucket name: {bucket_name}")
            return None
            
        # Generate a unique ID if not provided
        if not file_id:
            file_id = str(uuid.uuid4())
            
        # Get file extension
        _, ext = os.path.splitext(file_path)
        
        # Create full path with extension
        full_path = f"{file_id}{ext}"
        
        # Read file
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        # Upload to Supabase
        result = supabase.storage.from_(bucket_name).upload(
            path=full_path,
            file=file_data,
            file_options={"content_type": content_type} if content_type else None
        )
        
        if result:
            # Get public URL
            public_url = supabase.storage.from_(bucket_name).get_public_url(full_path)
            logger.info(f"File uploaded successfully: {public_url}")
            return public_url
        else:
            logger.error("File upload failed")
            return None
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return None

async def delete_file(file_path: str, bucket_name: str) -> bool:
    """
    Delete a file from Supabase Storage
    
    Args:
        file_path: Path to the file to delete
        bucket_name: Name of the bucket the file is in
        
    Returns:
        True if file was deleted, False otherwise
    """
    try:
        if bucket_name not in BUCKETS.values():
            logger.error(f"Invalid bucket name: {bucket_name}")
            return False
            
        # Delete from Supabase
        result = supabase.storage.from_(bucket_name).remove([file_path])
        
        if result:
            logger.info(f"File deleted successfully: {file_path}")
            return True
        else:
            logger.error("File deletion failed")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

async def get_file_url(file_path: str, bucket_name: str) -> Optional[str]:
    """
    Get the public URL of a file in Supabase Storage
    
    Args:
        file_path: Path to the file
        bucket_name: Name of the bucket the file is in
        
    Returns:
        Public URL of the file if it exists, None otherwise
    """
    try:
        if bucket_name not in BUCKETS.values():
            logger.error(f"Invalid bucket name: {bucket_name}")
            return None
            
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return public_url
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        return None