import logging
import os
from google.cloud import storage
from app.core.config import settings

logger = logging.getLogger(__name__)

class GCSClient:
    def __init__(self, bucket_name: str = ""):
        self.bucket_name = bucket_name
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        logger.debug(f"Initialized GCSClient with google-cloud-storage" + (f" for bucket: {bucket_name}" if bucket_name else ""))

    def download_file(self, gcs_uri: str, destination_path: str):
        """
        Download file from GCS to local path.
        Handles both 'gs://bucket/blob' format and plain 'blob' format.
        """
        if gcs_uri.startswith("gs://"):
            path_without_scheme = gcs_uri[5:]
            bucket_name, object_name = path_without_scheme.split('/', 1)
        else:
            bucket_name = self.bucket_name
            object_name = gcs_uri

        logger.debug(f"[GCS] Downloading gs://{bucket_name}/{object_name} -> {destination_path}")
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        try:
            # Use google-cloud-storage with credentials
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.download_to_filename(destination_path)
            logger.debug(f"[GCS] Successfully downloaded to {destination_path} using google-cloud-storage")
        except Exception as e:
            logger.error(f"[GCS] Failed to download {gcs_uri}: {e}")
            raise e

    def upload_file(self, local_path: str, gcs_uri: str):
        """
        Upload a local file to a GCS URI (gs://bucket/path/to/object).
        """
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Expected a gs:// URI, got: {gcs_uri}")

        path_without_scheme = gcs_uri[5:]
        bucket_name, object_name = path_without_scheme.split("/", 1)

        logger.debug(f"[GCS] Uploading {local_path} -> gs://{bucket_name}/{object_name}")

        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            blob.upload_from_filename(local_path)
            logger.debug(f"[GCS] Successfully uploaded to gs://{bucket_name}/{object_name}")
        except Exception as e:
            logger.error(f"[GCS] Failed to upload {local_path} to {gcs_uri}: {e}")
            raise e
