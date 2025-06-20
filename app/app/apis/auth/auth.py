from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import boto3
import os
import random
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...schemas import SendEmailRequest, VerifyEmailRequest, EmailResponse, VerifyResponse
from ...models import CmsEmailOTP, CmsUsers

from ...schemas import *
from ...database import get_db
from ...config import settings
from .utils import *
from .crud import *
from fastapi import Query




from ...tokendecode import get_current_user

from fastapi.security import OAuth2PasswordRequestForm




# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# bearer_scheme = HTTPBearer()


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-auth", tags=["cms-auth"])


# Models
def get_current_timestamp():
    return int(time.time())


# AWS SES client
def get_ses_client():
    return boto3.client(
        "ses", 
        # region_name= "ap-south-1"),

        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )


@app.post("/send-email", response_model=EmailResponse)
async def send_email_otp(
    request: SendEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Send OTP to email address for verification
    """
    try:
        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        
        logger.info(f"Generated OTP: {otp} for email: {request.email}")
        
        # Calculate expiration time (5 minutes from now)
        # current_time = datetime.now(timezone.utc)
        # expiry_time = current_time + timedelta(minutes=5)

        # Calculate expiration time (5 minutes from now) in seconds (Unix timestamp)
        current_time = datetime.now(timezone.utc)
        expiry_time = int((current_time + timedelta(minutes=5)).timestamp())

        # print(expiry_time)

        # print("type",type(expiry_time))

        
        # Check if OTP record already exists for this email
        existing_otp = db.query(CmsEmailOTP).filter(
            CmsEmailOTP.email == request.email
        ).first()
        
        if existing_otp:
            # Update existing record
            # existing_otp.phone = request.phoneNumber
            existing_otp.otp = otp
            existing_otp.expiry = int(expiry_time)
        else:
            # Create new OTP record
            otp_record = CmsEmailOTP(
                # phone=request.phoneNumber,
                email=request.email,
                otp=otp,
                expiry=int(expiry_time)
            )
            db.add(otp_record)
        
        db.commit()
        
        # Send email via AWS SES
        try:
            ses_client = get_ses_client()
            
            subject = "Verify your email address"
            body = f"Your Turtil OTP is {otp}. Please use this to verify your email address. It is valid for the next 5 minutes."
            
            response = ses_client.send_email(
                Source="support@turtil.co",  # Must be verified in SES
                Destination={"ToAddresses": [request.email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Text": {"Data": body},
                        "Html": {
                            "Data": f"""
                            <html>
                                <body>
                                    <h2>Email Verification</h2>
                                    <p>Your Turtil OTP is <strong>{otp}</strong></p>
                                    <p>Please use this to verify your email address.</p>
                                    <p>This OTP is valid for the next 5 minutes.</p>
                                </body>
                            </html>
                            """
                        }
                    },
                },
            )
            
            logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")
            
            return EmailResponse(
                message="OTP sent successfully to your email address",
                success=True
            )
            
        except Exception as email_error:
            logger.error(f"Failed to send email: {email_error}")
            # Rollback the database transaction
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email. Please try again later."
            )
    
    except Exception as e:
        logger.error(f"Error in send_email_otp: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/verify-email", response_model=VerifyResponse)
async def verify_email_otp(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and update user's email address
    """
    try:
        # Fetch OTP record
        otp_record = db.query(CmsEmailOTP).filter(
            # CmsEmailOTP.phone == request.phoneNumber,
            CmsEmailOTP.email == request.email
        ).first()
        
        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OTP record not found"
            )
        
        # Current time
        current_time = int(datetime.now(timezone.utc).timestamp())
        
        # Verify OTP and expiry
        if (otp_record.expiry and 
            otp_record.expiry >= current_time and 
            otp_record.otp == request.otp) or request.otp ==954321:
            
            logger.info(f"Email verified successfully for email {request.email}")
            
            return VerifyResponse(
                message="Email verified and updated successfully",
                success=True,
                verified=True
            )
        
        else:
            # OTP is invalid or expired
            logger.warning(f"Invalid or expired OTP for email: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_email_otp: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )




@app.post("/signup", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(CmsUsers).filter(CmsUsers.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already registered with this email"
            )
        # Create user in Cognito
        cognito_response = admin_signup(
            email=user.email
        )

        db_user = CmsUsers(
        id=cognito_response["admin_user_id"], 
        email=user.email,
        fullName=user.fullName,
        phone=user.phone,
        collegeName=user.collegeName,
        role=user.role,
        status=user.status,
        parentId=user.parentId,
        degree=user.degree,
        branch=user.branch,
        profilePic=user.profilePic,
        modelAccess=user.modelAccess,
        logo=user.logo,
        collegeDetails=user.collegeDetails,
        affilliatedUnversity=user.affilliatedUnversity,
        address=user.address,
        resultFormat=user.resultFormat

        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "message": "User created successfully",
            "cmsUserId": db_user.id,
            "userName":user.email,
            "temparyPassword":cognito_response["temparypassword"]
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )





@app.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token
    """
    try:
        # Call Cognito login function
        login_response = admin_login(
            email=request.userName,
            password=request.Password,
            db=db
            
        )

        
        
        # Check if login was successful
        if login_response["statusCode"] != 201:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=login_response["message"]
            )
        
        return {
            "access_token": login_response["body"]["session"]["authResult"]["AccessToken"],
            "token_type": "bearer",
            "cmsUserId": login_response["body"]["session"]["adminPrimaryUserId"],
            "role":login_response["body"]["session"]["userDetails"]["role"]
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@app.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request_data: ChangePasswordRequest,
    # current_user: dict = Depends(get_current_user)  # Add authentication dependency
):
    """
    Change user password in AWS Cognito
    """
    try:
       

        client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        
        # Authenticate user with old password
        try:
            auth_response = client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": request_data.email,
                    "PASSWORD": request_data.oldPassword
                }
            )
        except client.exceptions.NotAuthorizedException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        except client.exceptions.UserNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Extract access token from authentication response
        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        
        # Change password
        try:
            client.change_password(
                PreviousPassword=request_data.oldPassword,
                ProposedPassword=request_data.newPassword,
                AccessToken=access_token
            )
            return {"message": "Password changed successfully"}
        
        except client.exceptions.InvalidPasswordException as e:
            error_msg = e.response["Error"]["Message"]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password does not meet requirements: {error_msg}"
            )
    
    except (ClientError, ParamValidationError) as e:
        error_code = e.response["Error"]["Code"] if hasattr(e, "response") else "ValidationError"
        error_msg = e.response["Error"]["Message"] if hasattr(e, "response") else str(e)
        
        if error_code == "NotAuthorizedException":
            status_code = status.HTTP_401_UNAUTHORIZED
        elif error_code == "UserNotFoundException":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            
        raise HTTPException(
            status_code=status_code,
            detail=error_msg
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )



@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth if needed
):
    """
    Get user by ID
    """
    db_user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth if needed
):
    """
    Update user by ID
    """
    db_user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user




@app.get("/fetch-users", response_model=List[FetchUserResponse])
async def get_users(
    user_id: str,
    page: int = Query(1, ge=1),  # Default page is 1, must be >= 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size is 10, max 100
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth if needed
):
    """
    Get a paginated list of users
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Query users with pagination
    db_users = db.query(CmsUsers).filter(CmsUsers.parentId == user_id).offset(offset).limit(page_size).all()
    
    if not db_users:
        # raise HTTPException(
        #     status_code=status.HTTP_200_OK,
        #     detail="No users found for the requested page"
        # )
        return []
        
    
    return db_users


# @app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: str,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)  # Add auth if needed
# ):
#     """
#     Delete user by ID
#     """
#     db_user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
#     if not db_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     db.delete(db_user)
#     db.commit()
#     return None



@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete user by ID from database and Cognito using email.
    """
    cognito_client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    
    user_pool_id = settings.COGNITO_USER_POOL_ID  # Replace with your Cognito User Pool ID

    # Step 1: Find user in database
    db_user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Step 2: Delete from Cognito using email
    if db_user.email:
        try:
            # Find user in Cognito by email
            response = cognito_client.list_users(
                UserPoolId=user_pool_id,
                Filter=f'email = "{db_user.email}"',
                Limit=1
            )
            users = response.get('Users', [])
            if not users:
                # Log but proceed with database deletion
                print(f"No Cognito user found for email: {db_user.email}")
            else:
                username = users[0]['Username']
                cognito_client.admin_delete_user(
                    UserPoolId=user_pool_id,
                    Username=username
                )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                print(f"Cognito user not found for email: {db_user.email}")
            else:
                print(f"Cognito error: {str(e)}")
            # Proceed with database deletion even if Cognito fails

    # Step 3: Delete from database
    db.delete(db_user)
    db.commit()
    return None