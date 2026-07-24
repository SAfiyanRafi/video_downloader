from typing import List
from fastapi import APIRouter
from app.models.channel import ChannelProfile
from app.services.jobs.job_manager import job_manager

router = APIRouter()

@router.get("", response_model=List[ChannelProfile])
async def list_channels():
    """
    Returns a list of available channel profiles for intro/outro branding.
    """
    return job_manager.channel_service.get_all_channels()
