import math
from typing import List
from app.models.video import SegmentInfo

class EqualSplitService:
    """
    Calculates equal split points and timestamp ranges for a given duration and part count.
    Independent of downloading and FFmpeg rendering.
    """

    @staticmethod
    def calculate_splits(duration: float, parts: int) -> List[SegmentInfo]:
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")
        if parts < 2:
            raise ValueError("Parts must be at least 2")

        segment_duration = duration / parts
        segments: List[SegmentInfo] = []

        for i in range(parts):
            start_time = round(i * segment_duration, 3)
            # Ensure the final segment aligns exactly with full video duration
            end_time = round((i + 1) * segment_duration, 3) if i < parts - 1 else round(duration, 3)
            part_num = i + 1
            filename = f"part_{part_num:03d}.mp4"

            segments.append(
                SegmentInfo(
                    part_number=part_num,
                    start_time=start_time,
                    end_time=end_time,
                    duration=round(end_time - start_time, 3),
                    filename=filename
                )
            )

        return segments

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Formats seconds into HH:MM:SS.mmm for FFmpeg or display."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hrs:02d}:{mins:02d}:{secs:06.3f}"
