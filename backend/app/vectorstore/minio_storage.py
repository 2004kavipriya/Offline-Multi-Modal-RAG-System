"""
MinIO object storage client.
Handles file uploads and downloads.
"""

from minio import Minio
from minio.error import S3Error
from pathlib import Path
from typing import Optional
import logging
import io

from app.config import get_settings

logger = logging.getLogger(__name__)


class MinIOStorage:
    """MinIO object storage client."""
    
    def __init__(self):
        """Initialize MinIO client."""
        settings = get_settings()
        
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket()
        
        logger.info(f"MinIO client initialized for bucket: {self.bucket_name}")
    
    def _ensure_bucket(self):
        """Ensure the bucket exists."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket: {str(e)}")
            raise
    
    def upload_file(self, file_path: str, object_name: str, content_type: Optional[str] = None) -> str:
        """
        Upload a file to MinIO.
        
        Args:
            file_path: Path to the file to upload
            object_name: Name of the object in MinIO
            content_type: MIME type of the file
            
        Returns:
            Object name in MinIO
        """
        try:
            file_size = Path(file_path).stat().st_size
            
            with open(file_path, 'rb') as file_data:
                self.client.put_object(
                    self.bucket_name,
                    object_name,
                    file_data,
                    file_size,
                    content_type=content_type
                )
            
            logger.info(f"Uploaded file to MinIO: {object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {str(e)}")
            raise
    
    def upload_bytes(self, data: bytes, object_name: str, content_type: Optional[str] = None) -> str:
        """
        Upload bytes to MinIO.
        
        Args:
            data: Bytes to upload
            object_name: Name of the object in MinIO
            content_type: MIME type
            
        Returns:
            Object name in MinIO
        """
        try:
            data_stream = io.BytesIO(data)
            
            self.client.put_object(
                self.bucket_name,
                object_name,
                data_stream,
                len(data),
                content_type=content_type
            )
            
            logger.info(f"Uploaded bytes to MinIO: {object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"Error uploading bytes to MinIO: {str(e)}")
            raise
    
    def download_file(self, object_name: str, file_path: str):
        """
        Download a file from MinIO.
        
        Args:
            object_name: Name of the object in MinIO
            file_path: Path to save the file
        """
        try:
            self.client.fget_object(
                self.bucket_name,
                object_name,
                file_path
            )
            
            logger.info(f"Downloaded file from MinIO: {object_name}")
            
        except S3Error as e:
            logger.error(f"Error downloading file from MinIO: {str(e)}")
            raise
    
    def download_bytes(self, object_name: str) -> bytes:
        """
        Download object as bytes.
        
        Args:
            object_name: Name of the object in MinIO
            
        Returns:
            File contents as bytes
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            return data
            
        except S3Error as e:
            logger.error(f"Error downloading bytes from MinIO: {str(e)}")
            raise
    
    def delete_file(self, object_name: str):
        """
        Delete a file from MinIO.
        
        Args:
            object_name: Name of the object to delete
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted file from MinIO: {object_name}")
            
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {str(e)}")
            raise
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in MinIO.
        
        Args:
            object_name: Name of the object
            
        Returns:
            True if file exists
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def get_file_url(self, object_name: str, expires: int = 3600) -> str:
        """
        Get a presigned URL for a file.
        
        Args:
            object_name: Name of the object
            expires: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            from datetime import timedelta
            
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires)
            )
            
            return url
            
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise


# Global MinIO client instance
_minio_client = None


def get_minio_client() -> MinIOStorage:
    """Get the global MinIO client instance."""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOStorage()
    return _minio_client
