from typing import Optional

import bcrypt
import prisma
import prisma.models
from fastapi import HTTPException
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    """
    Defines the response structure upon successful user registration. Mainly includes user ID and email, ensuring that sensitive information like passwords are not included in the response.
    """

    id: str
    email: str
    role: str


async def create_user(
    email: str, password: str, role: Optional[str] = None
) -> UserRegistrationResponse:
    """
    Endpoint for user registration.

    Args:
    email (str): The email address for the user which serves as the username.
    password (str): The password for the user. It will be encrypted server-side for security.
    role (Optional[str]): The role assigned to the user upon registration, defaults to 'FREEUSER'.

    Returns:
    UserRegistrationResponse: Defines the response structure upon successful user registration. Mainly includes user ID and email, ensuring that sensitive information like passwords are not included in the response.
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    if not role:
        role = "FREEUSER"
    new_user = await prisma.models.User.prisma().create(
        data={"email": email, "password": hashed_password.decode("utf-8"), "role": role}
    )
    return UserRegistrationResponse(
        id=new_user.id, email=new_user.email, role=new_user.role
    )
