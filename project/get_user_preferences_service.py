from enum import Enum
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class QRCodeCustomizationSettings(BaseModel):
    """
    Defines the QR code customization preferences including size, color, error correction level, and formats.
    """

    size: int
    color: str
    errorCorrectionLevel: prisma.enums.ErrorCorrectionLevel
    format: List[prisma.enums.Format]


class GetUserPreferencesResponse(BaseModel):
    """
    Model for the response that contains the QR code customization preferences of the user. It encapsulates the settings in a structured format.
    """

    customizationPreferences: QRCodeCustomizationSettings


class ErrorCorrectionLevel(Enum):
    L: str = "L"
    M: str = "M"
    Q: str = "Q"
    H: str = "H"


class Format(Enum):
    SVG: str = "SVG"
    PNG: str = "PNG"
    JPEG: str = "JPEG"


async def get_user_preferences(userId: str) -> GetUserPreferencesResponse:
    """
    Retrieves saved QR code customization preferences for a user.

    Args:
    userId (str): The unique identifier of the user whose QR code customization preferences are being retrieved.

    Returns:
    GetUserPreferencesResponse: Model for the response that contains the QR code customization preferences of the user. It encapsulates the settings in a structured format.
    """
    customization_record = await prisma.models.Customization.prisma().find_unique(
        where={"QRCodeSettings": {"some": {"userId": userId}}}, include={"format": True}
    )
    if not customization_record:
        raise ValueError("Customization preferences not found for the given user ID.")
    customization_preferences = QRCodeCustomizationSettings(
        size=customization_record.size,
        color=customization_record.color,
        errorCorrectionLevel=prisma.enums.ErrorCorrectionLevel(
            customization_record.errorCorrection
        ),
        format=[prisma.enums.Format(fmt) for fmt in customization_record.format],
    )
    return GetUserPreferencesResponse(
        customizationPreferences=customization_preferences
    )
