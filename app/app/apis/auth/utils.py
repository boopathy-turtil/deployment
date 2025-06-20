import os
import boto3
from .helpers import *
from botocore.exceptions import ClientError, ParamValidationError
from fastapi import HTTPException, status
# from .dependencies import COGNITO_REGION, COGNITO_USER_POOL_ID
from ...config import settings
from sqlalchemy.orm import Session
from ...models import *



# def admin_signup(email: str):
#     try:
#         # Initialize Cognito client
#         client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
#         # Try to get existing user
#         existing_user = client.admin_get_user(
#             UserPoolId=settings.COGNITO_USER_POOL_ID,
#             Username=email
#         )
#         if existing_user:
#         # If found, return existing user ID
#             return {"admin_user_id": existing_user["Username"]}
        

#     except (ClientError, ParamValidationError) as e:
#         error_msg = e.response["Error"]["Message"] if isinstance(e, ClientError) else str(e)
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Cognito error: {error_msg}"
#         )

#         if error_code == "UserNotFoundException":
        
#         # Create user in Cognito
#         response_create_user = client.admin_create_user(
#             UserPoolId=settings.COGNITO_USER_POOL_ID,
#             Username=email,
#             UserAttributes=[
#                 {"Name": "email", "Value": email},
#                 {"Name": "email_verified", "Value": "true"}
#             ],
#             TemporaryPassword=generate_temp_password()
#             # MessageAction="SUPPRESS",
#         )
        
#         admin_user_id = response_create_user["User"]["Username"]
        
        # # Set permanent password
        # client.admin_set_user_password(
        #     UserPoolId=settings.COGNITO_USER_POOL_ID,
        #     Username=email,
        #     Password=password,
        #     Permanent=True,
        # )
        
#         return {"admin_user_id": admin_user_id}
    
#     except (ClientError, ParamValidationError) as e:
#         error_msg = e.response["Error"]["Message"] if isinstance(e, ClientError) else str(e)
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Cognito error: {error_msg}"
#         )
#     # except Exception as e:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#     #         detail="Internal server error"
#     #     )


# import boto3
# from botocore.exceptions import ClientError, ParamValidationError
# from fastapi import HTTPException, status

def admin_signup(email: str):
    try:
        # Initialize Cognito client
        # client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)

        client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
        
        # First check if user exists
        try:
            # Try to get existing user
            existing_user = client.admin_get_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=email
            )
            # temp = generate_temp_password()
            # # If found, return existing user ID
            # return {"admin_user_id": existing_user["Username"],
            #         "temparypassword":temp}
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="user already exist"
            )
            
        except client.exceptions.UserNotFoundException:
            # User doesn't exist - create new one
            temp = generate_temp_password()

            print("temparypassword", temp)
            response_create_user = client.admin_create_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"}
                ],
                TemporaryPassword=temp
            )
            admin_user_id = response_create_user["User"]["Username"]
             # Set permanent password
            client.admin_set_user_password(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=email,
                Password=temp,
                Permanent=True,
            )
            return {"admin_user_id": admin_user_id,
                    "temparypassword":temp}
    
    except (ClientError, ParamValidationError) as e:
        error_code = e.response["Error"]["Code"] if isinstance(e, ClientError) else "ValidationError"
        error_msg = e.response["Error"]["Message"] if isinstance(e, ClientError) else str(e)
        
        # Handle specific Cognito errors
        if error_code == "UserNotFoundException":
            # Shouldn't happen since we create if not found, but handle anyway
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found after creation attempt: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cognito error: {error_msg}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )




# def admin_login(email: str, password: str):
#     """
#     Logs in an existing user in AWS Cognito with email.
#     """
#     try:
#         user_pool_id =settings.COGNITO_USER_POOL_ID
#         client_id = os.environ["client_id"]
#         client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
#         if "email" not in request_json or "password" not in request_json:
#             return {
#                 "statusCode": 400,
#                 "message": "Email and password are required for email login.",
#                 "body": None,
#             }

#         username = email
#         password = password
#         auth_flow = "USER_PASSWORD_AUTH"
#         auth_parameters = {"USERNAME": username, "PASSWORD": password}

#         # Check if the user exists
#         get_user = client.admin_get_user(UserPoolId=user_pool_id, Username=username)

#         # Initiate the authentication flow
#         auth_response = client.initiate_auth(
#             ClientId=client_id,
#             AuthFlow=auth_flow,
#             AuthParameters=auth_parameters,
#         )

#         admin_user_id = get_user.get("Username", None)
#         # admin_response = db_queries.get_admin_details(admin_user_id)


#         # admin_user_name = admin_response.get("adminUserName")
#         # admin_user_type = admin_response.get("type", None)


#         session = {
#             "authResult": auth_response.get("AuthenticationResult"),
#             "adminPrimaryUserId": admin_user_id,
#             # "adminUserName": admin_user_name,
#             # "adminUserType": admin_user_type,

#         }

#         return {
#             "statusCode": 201,
#             "message": "User logged in successfully",
#             "body": {"session": session},
#         }

#     except client.exceptions.UserNotFoundException:
#         return {
#             "statusCode": 404,
#             "message": "User not found.",
#             "body": None,
#         }

#     except ParamValidationError as e:
#         return {"statusCode": 400, "message": str(e), "body": None}

#     except ClientError as e:
#         error_code = e.response["Error"]["Code"]
#         error_message = e.response["Error"]["Message"]
#         return {
#             "statusCode": 400,
#             "message": str(error_message),
#             "body": None,
#         }

#     except Exception as e:
#         return {
#             "statusCode": 400,
#             "message": str(e),
#             "body": None,
#         }



def get_db_user(db: Session, user_id: str):
    return db.query(CmsUsers).filter(CmsUsers.id == user_id).first()

def admin_login(email: str, password: str, db: Session):
    """
    Authenticate user with Cognito
    """
    try:
    # if 1:
        # client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)
        client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        user_pool_id = settings.COGNITO_USER_POOL_ID
        client_id = settings.COGNITO_CLIENT_ID
        
        # Check if user exists
        try:
            get_user = client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=email
            )
            admin_user_id = get_user["Username"]

            # print("admin_user_id", admin_user_id)
        except client.exceptions.UserNotFoundException:
            return {
                "statusCode": 404,
                "message": "User not found",
                "body": None
            }
        
        # Authenticate user
        auth_response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": email,
                "PASSWORD": password
            }
        )
        
        # Get additional user info from database
        # You'll need to implement get_db_user() based on your DB model
        db_user = get_db_user(db,admin_user_id)
        # db: Session
        # db_user =db.query(CmsUsers).filter(CmsUsers.id == admin_user_id).first()

        # print(db_user)
        
        return {
            "statusCode": 201,
            "message": "User logged in successfully",
            "body": {
                "session": {
                    "authResult": auth_response["AuthenticationResult"],
                    "adminPrimaryUserId": admin_user_id,
                    "userDetails": {
                        "fullName": db_user.fullName,
                        "email": db_user.email,
                        "role": db_user.role
                        # "role": "superAdmin"

                    }
                }
            }
        }
    
    except client.exceptions.NotAuthorizedException:
        return {
            "statusCode": 401,
            "message": "Incorrect username or password",
            "body": None
        }
    except client.exceptions.UserNotConfirmedException:
        return {
            "statusCode": 401,
            "message": "User not confirmed",
            "body": None
        }
    except (ClientError, ParamValidationError) as e:
        error_msg = e.response["Error"]["Message"] if hasattr(e, "response") else str(e)
        return {
            "statusCode": 400,
            "message": f"Cognito error: {error_msg}",
            "body": None
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "message": f"Internal server error: {str(e)}",
            "body": None
        }





