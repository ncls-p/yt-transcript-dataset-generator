"""YouTube video downloading logic."""

from typing import Optional


def get_video_id(url: str) -> Optional[str]:
    """
    Extract the YouTube video ID from a URL.
    Args:
        url: The YouTube video URL.
    Returns:
        The video ID if found, else None.
    """
    if "youtube.com/watch?v=" in url:
        return url.split("v=")[-1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


def download_video(url: str, output_dir: str) -> Optional[str]:
    """
    Download a YouTube video to the specified output directory.
    Args:
        url: The YouTube video URL.
        output_dir: Directory to save the downloaded video.
    Returns:
        The path to the downloaded video file, or None if failed.
    """
    import os

    import yt_dlp

    os.makedirs(output_dir, exist_ok=True)
    outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    ydl_opts = {"format": "best", "outtmpl": outtmpl, "quiet": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info and "title" in info and "ext" in info:
                filename = f"{info['title']}.{info['ext']}"
                return os.path.join(output_dir, filename)
    except Exception as e:
        print(f"Error downloading video from {url}: {e}")
    return None
