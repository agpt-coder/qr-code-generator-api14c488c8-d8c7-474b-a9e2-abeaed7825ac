from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UpdateUserPreferencesResponse(BaseModel):
    """
    Response model to confirm successful updating of user-specific QR code customization preferences.
    """

    success: bool
    message: str


async def update_user_preferences(
    userId: str,
    size: int,
    color: str,
    errorCorrection: prisma.enums.ErrorCorrectionLevel,
    outputFormat: List[prisma.enums.Format],
) -> UpdateUserPreferencesResponse:
    """
    Updates user-specific QR code customization preferences.

    Args:
        userId (str): Path parameter representing the unique identifier for the user whose preferences are being updated.
        size (int): Desired size for the QR code.
        color (str): Preferred color for the QR code.
        errorCorrection (prisma.enums.ErrorCorrectionLevel): Error correction level to be applied to the QR code.
        outputFormat (List[prisma.enums.Format]): prisma.enums.Format in which the QR code should be outputted.

    Returns:
        UpdateUserPreferencesResponse: Response model to confirm successful updating of user-specific QR code customization preferences.

    """
    qrcode_setting = await prisma.models.QRCodeSettings.prisma().find_first(
        where={"userId": userId}, include={"customization": True}
    )
    if qrcode_setting:
        await prisma.models.Customization.prisma().update(
            where={"id": qrcode_setting.customizationId},
            data={
                "size": size,
                "color": color,
                "errorCorrection": errorCorrection,
                "format": {"set": outputFormat},
            },
        )
    else:
        new_customization = await prisma.models.Customization.prisma().create(
            data={
                "size": size,
                "color": color,
                "errorCorrection": errorCorrection,
                "format": outputFormat,
                "QRCodeSettings": {"create": {"User": {"connect": {"id": userId}}}},
            }
        )
    return UpdateUserPreferencesResponse(
        success=True, message="User preferences updated successfully."
    )
