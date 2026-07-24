import logging
from typing import List, Dict
from pydantic import BaseModel

logger = logging.getLogger("yt_splitter")

class AIContentSuggestions(BaseModel):
    titles: List[str]
    description: str
    hashtags: List[str]
    chapters: List[str]

class AIContentHelper:
    """
    AI Content & Upload Preparation Engine:
    - Generates title options, descriptions, hashtags, and chapter markers.
    """
    def generate_suggestions(self, video_title: str, transcript_text: str = "") -> AIContentSuggestions:
        clean_title = video_title.replace("_", " ").strip()
        
        titles = [
            f"🔥 {clean_title} — Must Watch!",
            f"What Happens In {clean_title}? (Full Breakdown)",
            f"The Ultimate Guide to {clean_title} 🚀"
        ]

        description = (
            f"Enjoy this clip from {clean_title}!\n\n"
            f"📌 Subscribe for more high-quality clips & shorts updates.\n"
            f"LIKE, SHARE & COMMENT below your favorite moments!"
        )

        hashtags = ["#Shorts", "#Viral", "#Trending", "#YouTube", "#Reels", "#TikTok"]

        chapters = [
            "00:00 - Introduction & Key Hook",
            "00:30 - Main Highlights & Key Moment",
            "01:30 - Final Conclusion & Call To Action"
        ]

        return AIContentSuggestions(
            titles=titles,
            description=description,
            hashtags=hashtags,
            chapters=chapters
        )

ai_content_helper = AIContentHelper()
