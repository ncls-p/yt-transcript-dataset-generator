"""Unit tests for transcript module."""

from src.transcript import get_video_transcript


def test_get_video_transcript_invalid_id():
    assert get_video_transcript("invalid_id_123456") is None
