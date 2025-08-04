"""Dataset CSV processing logic."""

import csv
import os
from typing import Dict, List


def write_dataset_csv(
    dataset_rows: List[Dict[str, object]], dataset_csv_path: str
) -> str:
    """
    Write a list of dataset rows to a CSV file.
    Args:
        dataset_rows: List of dictionaries containing dataset information.
        dataset_csv_path: Path to the output CSV file.
    Returns:
        The path to the written CSV file.
    """
    os.makedirs(os.path.dirname(dataset_csv_path), exist_ok=True)
    fieldnames = [
        "url",
        "video_id",
        "title",
        "mp4_path",
        "mp3_path",
        "transcript_path",
        "transcript_exists",
        "transcript",
    ]
    with open(dataset_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in dataset_rows:
            writer.writerow(row)
    return dataset_csv_path
