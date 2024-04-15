import prisma
import prisma.models
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel


class UserLoginResponse(BaseModel):
    """
    This model represents the response payload after a successful login. It contains authentication tokens necessary for accessing protected endpoints.
    """

    access_token: str
    refresh_token: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def user_login(email: str, password: str) -> UserLoginResponse:
    """
    Endpoint for user login, returning authentication tokens.

    This function checks if the provided email and password match a user in the database.
    If a match is found, it generates authentication tokens (access and refresh tokens)
    that are returned to the user for subsequent requests authentication.

    Args:
        email (str): The user's email address used for login.
        password (str): The user's password.

    Returns:
        UserLoginResponse: This model represents the response payload after a successful login. It contains authentication tokens necessary for accessing protected endpoints.

    Raises:
        HTTPException: If the credentials are invalid or the user is not found.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = jwt.encode({"sub": user.email}, "secret_access", algorithm="HS256")
    refresh_token = jwt.encode({"sub": user.email}, "secret_refresh", algorithm="HS256")
    return UserLoginResponse(access_token=access_token, refresh_token=refresh_token)
