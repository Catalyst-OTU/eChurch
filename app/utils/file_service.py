from google.cloud import storage
from config.settings import settings

def get_gcs_client():
    credentials_info = settings.GCS_CREDENTIALS  # Already parsed as a dict
    return storage.Client.from_service_account_info(credentials_info)

client = get_gcs_client()

def upload_to_gcs(files: list, folder: str) -> dict:
    bucket = client.get_bucket(settings.GCP_BUCKET_NAME)
    public_urls = {}

    for file in files:
        storage_path = f'appraisal/{folder}/{file["filename"]}'
        blob = bucket.blob(storage_path)
        try:
            from io import BytesIO
            file_content = BytesIO(file['content'])
            blob.upload_from_file(file_content, content_type="image/*")
            public_urls[file['filename']] = f'https://storage.googleapis.com/{settings.GCP_BUCKET_NAME}/{storage_path}'
        except Exception as e:
            # Log the error and continue processing next file
            continue

    return public_urls
