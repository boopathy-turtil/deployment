import secrets

# Generate a 32-character (or longer) random secret key
secret_key = secrets.token_hex(32)
print(secret_key)



from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Depends, status




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode token without verification for demo
        # In production, use proper secret and algorithm
        payload = jwt.decode(token, None, options={"verify_signature": False})
        user_id = payload.get("username")  # Cognito stores user ID in 'username'
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
    


username = "abc@gmail.com"
temparypassword= "MQE^bYU+7zng"

{
  "email": "abc@gmail.com",
  "oldPassword": "MQE^bYU+7zng",
  "newPassword": "NewP@ssw0rd2023!"
}

{
  "userName": "abc@gmail.com",
  "Password": "NewP@ssw0rd2023!"
}

{
  "userName": "8421@gmail.com",
  "Password": "Noxz7q!%%1jo"
}

{
"userName": "string@gmail.com",
"Password": "=7GUY-Nz$(3i"
}


{
 
  "userName": "string1190@gmail.com",
  "Password": "zVH!XFbwWD0N"
}

{
 
  "userName": "raj119@gmail.com",
  "Password": "qCMAU2h_Z5W@"
}

[
  {
    "degreeLevel": "Undergraduate (UG)",
    "degrees": ["B.Tech (Bachelor of Technology)", "B.E. (Bachelor of Engineering)"]
  },
  {
    "degreeLevel": "Postgraduate (PG)",
    "degrees": ["M.Tech (Master of Technology)", "M.E. (Master of Engineering)"]
  },
  {
    "degreeLevel": "Diploma",
    "degrees": ["Diploma in Engineering"]
  }
]


{
  "collegeId": "JBREC001",
  "collegeShortName": "JBREC",
  "collegeName": "JBREC",
  "studentId": "15j21a0580",
  "studentName": "raj",
  "email": "raj@gmail.com",
  "phone": "9550123456",
  "degree": "b-tech",
  "batch": "2015",
  "branch": "cse",
  "section": "a",
  "gender": "male"
}