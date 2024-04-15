import logging
from contextlib import asynccontextmanager
from typing import List, Optional

import prisma
import prisma.enums
import project.create_user_service
import project.generate_qr_code_service
import project.get_user_preferences_service
import project.update_user_preferences_service
import project.user_login_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="QR Code Generator API",
    lifespan=lifespan,
    description="The task at hand involves creating a feature within an application that allows users to generate QR codes based on specific inputs and preferences. The inputs can include data such as URLs, text, contact information, etc. The user desires the ability to customize the generated QR code in several ways, including its size, color, and error correction level (L, M, Q, H), with a preference for 'Q' level error correction. Additionally, the QR code image must be returnable in different formats, with SVG being the preferred format.\n\nGiven this scope, the recommended tech stack for implementing this feature would include Python as the programming language due to its excellent support for image manipulation and generation libraries, FastAPI as the API framework for its speed and ease of use in building API endpoints, PostgreSQL for storing any necessary data such as user preferences or the data to be encoded, and Prisma as the ORM for efficient database interactions. Essential steps involved in executing this task would include setting up an API endpoint that accepts the user's input data and preferences, utilizing a QR code generation library in Python to create the QR code based on these inputs, and finally, serving the generated QR code image back to the user in the specified format.",
)


@app.post("/users", response_model=project.create_user_service.UserRegistrationResponse)
async def api_post_create_user(
    email: str, password: str, role: Optional[str]
) -> project.create_user_service.UserRegistrationResponse | Response:
    """
    Endpoint for user registration.
    """
    try:
        res = await project.create_user_service.create_user(email, password, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users/login", response_model=project.user_login_service.UserLoginResponse)
async def api_post_user_login(
    email: str, password: str
) -> project.user_login_service.UserLoginResponse | Response:
    """
    Endpoint for user login, returning authentication tokens.
    """
    try:
        res = await project.user_login_service.user_login(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/users/{userId}/preferences",
    response_model=project.update_user_preferences_service.UpdateUserPreferencesResponse,
)
async def api_put_update_user_preferences(
    userId: str,
    size: int,
    color: str,
    errorCorrection: prisma.enums.ErrorCorrectionLevel,
    outputFormat: List[prisma.enums.Format],
) -> project.update_user_preferences_service.UpdateUserPreferencesResponse | Response:
    """
    Updates user-specific QR code customization preferences.
    """
    try:
        res = await project.update_user_preferences_service.update_user_preferences(
            userId, size, color, errorCorrection, outputFormat
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/{userId}/preferences",
    response_model=project.get_user_preferences_service.GetUserPreferencesResponse,
)
async def api_get_get_user_preferences(
    userId: str,
) -> project.get_user_preferences_service.GetUserPreferencesResponse | Response:
    """
    Retrieves saved QR code customization preferences for a user.
    """
    try:
        res = await project.get_user_preferences_service.get_user_preferences(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/qr/generate",
    response_model=project.generate_qr_code_service.QRCodeGenerateResponse,
)
async def api_post_generate_qr_code(
    data: str, size: int, color: str, error_correction: str, output_format: str
) -> project.generate_qr_code_service.QRCodeGenerateResponse | Response:
    """
    Main endpoint for creating QR codes based on dynamic user inputs and preferences.
    """
    try:
        res = project.generate_qr_code_service.generate_qr_code(
            data, size, color, error_correction, output_format
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
