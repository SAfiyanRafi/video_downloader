import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from app.models.channel import ChannelProfile

logger = logging.getLogger("yt_splitter")

class ChannelService:
    def __init__(self, root_dir: Optional[Path] = None):
        if root_dir is None:
            # f:\Platform
            root_dir = Path(__file__).resolve().parents[4]
        self.root_dir = root_dir
        self.config_path = self.root_dir / "assets" / "channels" / "channels.json"
        self.channels: Dict[str, ChannelProfile] = {}
        self._load_channels()

    def _load_channels(self):
        if not self.config_path.exists():
            logger.warning(f"Channel config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for channel_id, cfg in data.items():
                profile = ChannelProfile(
                    id=channel_id,
                    display_name=cfg.get("display_name", channel_id),
                    intro=cfg.get("intro"),
                    outro=cfg.get("outro"),
                    filename_prefix=cfg.get("filename_prefix", channel_id),
                    watermark=cfg.get("watermark"),
                    logo=cfg.get("logo"),
                    thumbnail=cfg.get("thumbnail"),
                    resolution=cfg.get("resolution", "1080p"),
                    format=cfg.get("format", "mp4"),
                    normalize_audio=cfg.get("normalize_audio", True),
                    default_quality=cfg.get("default_quality", "best")
                )
                self.channels[channel_id] = profile

            logger.info(f"Loaded {len(self.channels)} channel profiles from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to parse channel profiles: {e}", exc_info=True)

    def get_all_channels(self) -> List[ChannelProfile]:
        # Always reload config in case user added a channel folder/config
        self._load_channels()
        return list(self.channels.values())

    def get_channel(self, channel_id: str) -> ChannelProfile:
        self._load_channels()
        profile = self.channels.get(channel_id)
        if not profile:
            raise KeyError(f"Channel profile '{channel_id}' does not exist.")
        return profile

    def validate_channel_assets(self, channel_id: str) -> ChannelProfile:
        profile = self.get_channel(channel_id)

        if profile.intro:
            intro_path = self.root_dir / profile.intro
            if not intro_path.exists():
                raise FileNotFoundError(f"Intro video for channel '{channel_id}' not found at {intro_path}")

        if profile.outro:
            outro_path = self.root_dir / profile.outro
            if not outro_path.exists():
                raise FileNotFoundError(f"Outro video for channel '{channel_id}' not found at {outro_path}")

        return profile
