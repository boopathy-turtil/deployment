# import os
# import boto3
# from botocore.exceptions import ClientError, ParamValidationError
# from fastapi import HTTPException, status
# # from .dependencies import COGNITO_REGION, COGNITO_USER_POOL_ID
# from ...config import settings
# from sqlalchemy.orm import Session
# from ...models import *
# import logging
# from fastapi import APIRouter, Depends, HTTPException, status



# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = APIRouter(prefix="/cms-image-upload", tags=["cms-image-upload"])



# def generate_presigned_url(request_json, route, host):
#     try:
#         # Initialize the S3 client
#         s3 = boto3.client("s3",region_name=settings.COGNITO_REGION,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

#         # Bucket name and object key
#         bucket_name = settings.STUDENT_DOCUMENT
#         # bucket_name = "dev-std-student-images"

#         files = request_json["file_name"]

#         object_key = files

#         # Allowed file types and their corresponding MIME types
#         ALLOWED_FILE_TYPES = {
#             "jpg": "image/jpeg",
#             "jpeg": "image/jpeg",
#             "png": "image/png",
#             "pdf": "application/pdf",
#             "doc": "application/msword",
#             "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#         }

#         # Determine file extension from the filename
#         file_extension = files.split(".")[-1].lower()

#         # if file_extension not in ALLOWED_FILE_TYPES:
#         #     return {
#         #         "statusCode": 400,
#         #         "message": "Invalid file type. Only JPG, JPEG, PNG, PDF, DOC, and DOCX are allowed.",
#         #         "body": None,
#         #     }

#         # Generate a pre-signed URL for the S3 object with PutObject permission
#         url = s3.generate_presigned_url(
#             ClientMethod="put_object",
#             Params={"Bucket": bucket_name, "Key": object_key},
#             ExpiresIn=3600,
#             HttpMethod="PUT",
#         )

#         return {
#             "statusCode": 200,
#             "message": "Pre-signed URL retrieved successfully",
#             "body": {"presigned_url": url},
#         }

#     except ClientError as e:
#         return {
#             "statusCode": 500,
#             "message": "Error generating presigned URL",
#             "body": None,
#         }

#     except KeyError as e:
#         return {
#             "statusCode": 400,
#             "message": "Missing required key",
#             "body": None,
#         }
#     except Exception as e:
#         logger.error("Error: %s", e)
#         return {
#             "statusCode": 500,
#             "message": "Internal server error",
#             "body": None,
#         }



from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
import logging
from ...config import settings
from typing import Optional
from ...schemas import PresignedUrlResponse, PresignedUrlRequest


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-image-upload", tags=["cms-image-upload"])

@app.post("/generate-presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url_endpoint(
    request: PresignedUrlRequest
):
    """
    Generate a pre-signed S3 URL for uploading a file.
    """
    try:
        # Initialize the S3 client
        s3 = boto3.client(
            "s3",
            region_name=settings.COGNITO_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        # Bucket name and object key
        # bucket_name = settings.STUDENT_DOCUMENT
        bucket_name = "my-cms-image-upload"
        # bucket_name = "dev-std-student-images"

        files = request.file_name

        print(files)

        object_key = files

        # Allowed file types and their corresponding MIME types
        ALLOWED_FILE_TYPES = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "pdf": "application/pdf",
            "doc": "application/msword",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        # Determine file extension from the filename
        file_extension = files.split(".")[-1].lower()

        # Generate a pre-signed URL for the S3 object with PutObject permission
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=3600,
            HttpMethod="PUT",
        )

        return {
            "statusCode": 200,
            "message": "Pre-signed URL retrieved successfully",
            "body": {"presigned_url": url},
        }


    except ClientError as e:
        logger.error("ClientError: %s", e)
        return PresignedUrlResponse(
            statusCode=500,
            message="Error generating presigned URL",
            body=None
        )

    except KeyError as e:
        logger.error("KeyError: %s", e)
        return PresignedUrlResponse(
            statusCode=400,
            message="Missing required key",
            body=None
        )

    except Exception as e:
        logger.error("Error: %s", e)
        return PresignedUrlResponse(
            statusCode=500,
            message="Internal server error",
            body=None
        )


# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel
# import boto3
# from botocore.exceptions import ClientError
# import logging
# from typing import Optional

# # Assuming settings and schemas are defined elsewhere
# from ...config import settings
# from ...schemas import PresignedUrlResponse, PresignedUrlRequest

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = APIRouter(prefix="/cms-image-upload", tags=["cms-image-upload"])

# @app.post("/generate-presigned-url", response_model=PresignedUrlResponse)
# async def generate_presigned_url_endpoint(request: PresignedUrlRequest):
#     """
#     Generate a pre-signed S3 URL for uploading a file.
#     """
#     try:
#         # Initialize the S3 client
#         s3 = boto3.client(
#             "s3",
#             region_name=settings.COGNITO_REGION,
#             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
#         )

#         # Bucket name and object key
#         bucket_name = settings.STUDENT_DOCUMENT
#         object_key = request.file_name

#         # Allowed file types and their corresponding MIME types
#         ALLOWED_FILE_TYPES = {
#             "jpg": "image/jpeg",
#             "jpeg": "image/jpeg",
#             "png": "image/png",
#             "pdf": "application/pdf",
#             "doc": "application/msword",
#             "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#         }

#         # Determine file extension from the filename
#         file_extension = object_key.split(".")[-1].lower()

#         if file_extension not in ALLOWED_FILE_TYPES:
#             return PresignedUrlResponse(
#                 statusCode=400,
#                 message="Invalid file type. Only JPG, JPEG, PNG, PDF, DOC, and DOCX are allowed.",
#                 body=None
#             )

#         # Generate a pre-signed URL for the S3 object with PutObject permission
#         url = s3.generate_presigned_url(
#             ClientMethod="put_object",
#             Params={
#                 "Bucket": bucket_name,
#                 "Key": object_key,
#                 "ContentType": ALLOWED_FILE_TYPES[file_extension]
#             },
#             ExpiresIn=3600,
#             HttpMethod="PUT",
#         )

#         return PresignedUrlResponse(
#             statusCode=200,
#             message="Pre-signed URL retrieved successfully",
#             body={"presigned_url": url}
#         )

#     except ClientError as e:
#         logger.error("ClientError: %s", e)
#         return PresignedUrlResponse(
#             statusCode=500,
#             message=f"Error generating presigned URL: {str(e)}",
#             body=None
#         )

#     except KeyError as e:
#         logger.error("KeyError: %s", e)
#         return PresignedUrlResponse(
#             statusCode=400,
#             message="Missing required key",
#             body=None
#         )

#     except Exception as e:
#         logger.error("Error: %s", e)
#         return PresignedUrlResponse(
#             statusCode=500,
#             message="Internal server error",
#             body=None
#         )