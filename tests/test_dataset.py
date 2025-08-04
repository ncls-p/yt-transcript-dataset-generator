"""Unit tests for dataset module."""

import os

from src.dataset import write_dataset_csv


def test_write_dataset_csv(tmp_path):
    dataset_rows = [
        {
            "url": "https://youtu.be/test",
            "video_id": "test",
            "title": "Test Video",
            "mp4_path": "test.mp4",
            "mp3_path": "test.mp3",
            "transcript_path": "test.txt",
            "transcript_exists": True,
            "transcript": "Hello world",
        }
    ]
    csv_path = tmp_path / "dataset.csv"
    result = write_dataset_csv(dataset_rows, str(csv_path))
    assert os.path.exists(result)
    with open(result, encoding="utf-8") as f:
        content = f.read()
    assert "Test Video" in content
