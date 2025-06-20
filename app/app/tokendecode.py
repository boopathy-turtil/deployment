

# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from fastapi import FastAPI, HTTPException, Depends, status
# from typing import Annotated, Optional

# from .config import settings

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# bearer_scheme = HTTPBearer()



# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
#     try:
#         # Decode token without verification for demo
#         # In production, use proper secret and algorithm
#         token = credentials.credentials  # Extract token string
#         payload = jwt.decode(token, None, options={"verify_signature": False})

#         # payload = jwt.decode(
#         #     token,
#         #     key=get_public_key(token),
#         #     algorithms=["RS256"],
#         #     audience=settings.COGNITO_CLIENT_ID
#         # )
#         user_id = payload.get("username")  # Cognito stores user ID in 'username'
#         if user_id is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid authentication credentials"
#             )
#         return {"user_id": user_id}
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )


from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt, jwk
import requests
from typing import Annotated
from .config import settings

bearer_scheme = HTTPBearer()

def get_public_key(token: str) -> str:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    jwks_url = f"https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    jwks = response.json()

    for key in jwks["keys"]:
        if key["kid"] == kid:
            return jwk.construct(key).to_pem().decode("utf-8")
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No matching public key found"
    )

def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            key=get_public_key(token),
            algorithms=["RS256"],
            audience=settings.COGNITO_CLIENT_ID
        )
        user_id = payload.get("username")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )