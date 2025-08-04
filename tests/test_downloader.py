"""Unit tests for downloader module."""

from src.downloader import get_video_id


def test_get_video_id_youtube_url():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert get_video_id(url) == "dQw4w9WgXcQ"


def test_get_video_id_short_url():
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert get_video_id(url) == "dQw4w9WgXcQ"


def test_get_video_id_invalid_url():
    url = "https://example.com/"
    assert get_video_id(url) is None
