"""Unit tests for converter module."""

import pytest

from src.converter import mp4_to_mp3


def test_mp4_to_mp3_invalid_file(tmp_path):
    mp4_path = tmp_path / "not_a_video.mp4"
    mp3_path = tmp_path / "output.mp3"
    mp4_path.write_text("not a real video")
    with pytest.raises(Exception):
        mp4_to_mp3(str(mp4_path), str(mp3_path))
