"""YouTube transcript fetching logic."""

from typing import Optional


def get_video_transcript(video_id: str) -> Optional[str]:
    """
    Fetch the transcript for a YouTube video by its ID.
    Args:
        video_id: The YouTube video ID.
    Returns:
        The transcript as a string if available, else None.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        transcript = YouTubeTranscriptApi().fetch(video_id, languages=["fr", "en"])
        return " ".join(snippet.text for snippet in transcript)
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
