from typing import List
from fastapi import APIRouter
from app.models.channel import ChannelProfile
from app.services.branding.channel_service import ChannelService

router = APIRouter()
channel_service = ChannelService()

@router.get("", response_model=List[ChannelProfile])
async def list_channels():
    """
    Returns a list of available channel profiles.
    """
    return channel_service.get_all_channels()
