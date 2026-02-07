# import functools
# import json
# import os
# from typing import Literal
#
# from fastapi import HTTPException
# from google.auth.exceptions import DefaultCredentialsError
# from google.cloud import storage
# from starlette.datastructures import UploadFile
#
# from config.logger import log
# from config.settings import settings
#
#
# def handle_credential_error(func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except DefaultCredentialsError:
#             log.error("Failed to get credentials from GCS", exc_info=True)
#             raise HTTPException(status_code=500, detail="Failed to get credentials from GCS")
#         except:
#             log.exception("Failed to upload file to GCS")
#             raise HTTPException(status_code=500, detail="Failed to upload file to GCS")
#
#     return wrapper
#
#
# class GCSFileHelper:
#     """GOOGLE CLOUD FILE UPLOAD"""
#
#     def __init__(self, client: storage.Client = None):
#         if client is None: client = self._get_client()
#         self.client = client
#
#     @handle_credential_error
#     def upload(
#             self,
#             file: UploadFile,
#             file_type: Literal["AUDIO", "VIDEO", "IMAGE", "DOCUMENT"]
#     ) -> str:
#         if file_type not in ["AUDIO", "VIDEO", "IMAGE", "DOCUMENT"]: raise ValueError(
#             f"Expected 'AUDIO' or 'VIDEO' or 'IMAGE' or 'DOCUMENT' but got {file_type}"
#         )
#         bucket = self.client.get_bucket(settings.GCP_BUCKET_NAME)
#         file_path = self._get_file_path(file_type) + "/" + file.filename
#         blob = bucket.blob(file_path)
#         blob.upload_from_file(file.file)
#         blob.make_public()
#         return file_path
#
#     @handle_credential_error
#     def stream(self, path) -> bytes:
#         bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
#         blob = bucket.blob(path)
#         file = blob.download_as_bytes()
#         return file
#
#     @handle_credential_error
#     def delete(self, filename: str):
#         bucket = self.client.get_bucket(settings.BUCKET_NAME)
#         flyer_path = settings.GCP_FILE_PATH + "/" + filename
#         blob = bucket.blob(flyer_path)
#         blob.delete()
#
#     @staticmethod
#     def _get_client():
#         # Get the path to the Google Cloud API JSON file from an environment variable
#         # Check if the GOOGLE_APPLICATION_CREDENTIALS file exists.
#         gcloud_credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
#
#         if gcloud_credentials_path and os.path.exists(gcloud_credentials_path):
#             with open(gcloud_credentials_path) as f:
#                 credentials_info = json.load(f)
#         else:
#             credentials_info = settings.GCS_CREDENTIALS
#             if not credentials_info or "private_key" not in credentials_info:
#                 raise ValueError("Invalid or missing GCS credentials.")
#
#         return storage.Client.from_service_account_info(
#             credentials_info,
#             project=credentials_info.get("project_id")
#         )
#
#     # @staticmethod
#     # def _get_file_path(file_type: Literal["AUDIO", "VIDEO", "IMAGE", "DOCUMENT"]) -> str:
#     #     if file_type not in ["AUDIO", "VIDEO", "IMAGE", "DOCUMENT"]: raise ValueError(
#     #         f"Expected 'AUDIO' or 'VIDEO' or 'IMAGE' or 'DOCUMENT' but got {file_type}"
#     #     )
#     #     match file_type:
#     #         case "AUDIO":
#     #             path = settings.AUDIO_PATH
#     #         case "VIDEO":
#     #             path = settings.VIDEO_PATH
#     #         case "IMAGE":
#     #             path = settings.IMAGE_PATH
#     #         case "DOCUMENT":
#     #             path = settings.DOCUMENT_PATH
#     #         case _:
#     #             raise ValueError(f"Expected 'AUDIO' or 'VIDEO' or 'IMAGE' or 'DOCUMENT' got {file_type}")
#     #     return path or ""
