"""MP4 to MP3 conversion logic."""


def mp4_to_mp3(mp4_path: str, mp3_path: str) -> None:
    """
    Convert an MP4 video file to an MP3 audio file.
    Args:
        mp4_path: Path to the input MP4 file.
        mp3_path: Path to the output MP3 file.
    """
    from moviepy import VideoFileClip

    with VideoFileClip(mp4_path) as video:
        if video.audio is not None:
            video.audio.write_audiofile(mp3_path, codec="mp3")
