"""
Main orchestrator for the YouTube video processing pipeline.
Coordinates downloading videos, converting to MP3, fetching transcripts, and writing the dataset CSV.
Follows Clean Code and Clean Architecture principles.
"""

import csv
import json
import os
from typing import Any, Dict, List

from tqdm import tqdm

from src.converter import mp4_to_mp3
from src.dataset import write_dataset_csv
from src.downloader import download_video, get_video_id
from src.qa import generate_qa_pairs
from src.utils import sanitize_transcript
from src.transcript import get_video_transcript

DATASET_CSV_PATH = "dataset/dataset.csv"
VIDEOS_CSV_PATH = "videos.csv"
OUTPUT_MP4_DIR = "dataset/output_mp4"
OUTPUT_MP3_DIR = "dataset/output_mp3"
OUTPUT_TRANSCRIPTS_DIR = "dataset/output_transcripts"


def process_videos_from_csv(
    csv_path: str,
    video_output_dir: str,
    audio_output_dir: str,
    transcript_output_dir: str,
    dataset_csv_path: str,
) -> str:
    """
    Process YouTube videos listed in a CSV file:
    - Download videos
    - Convert to MP3
    - Fetch and sanitize transcripts
    - Generate Q&A pairs
    - Write results to a dataset CSV

    Args:
        csv_path: Path to input CSV with YouTube URLs.
        video_output_dir: Directory to save downloaded MP4s.
        audio_output_dir: Directory to save converted MP3s.
        transcript_output_dir: Directory to save transcripts.
        dataset_csv_path: Path to output dataset CSV.
    Returns:
        Path to the generated dataset CSV.
    """
    dataset_rows: List[Dict[str, Any]] = []
    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(audio_output_dir, exist_ok=True)
    os.makedirs(transcript_output_dir, exist_ok=True)

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        for row in tqdm(reader, desc="Processing videos", unit="video"):
            url = row.get("url", "").strip()
            if not url:
                continue
            video_id = get_video_id(url)
            title = None
            mp4_path = None
            mp3_path = None
            transcript_path = None
            transcript = None
            transcript_exists = False

            if video_id:
                possible_mp4s = [
                    f
                    for f in os.listdir(video_output_dir)
                    if f.endswith(".mp4") and video_id in f
                ]
                if possible_mp4s:
                    mp4_path = os.path.join(video_output_dir, possible_mp4s[0])
                    title = os.path.splitext(os.path.basename(mp4_path))[0]
                else:
                    mp4_path = download_video(url, video_output_dir)
                    title = (
                        os.path.splitext(os.path.basename(mp4_path))[0]
                        if mp4_path
                        else ""
                    )
            else:
                mp4_path = download_video(url, video_output_dir)
                title = (
                    os.path.splitext(os.path.basename(mp4_path))[0] if mp4_path else ""
                )

            mp3_path = os.path.join(audio_output_dir, f"{title}.mp3") if title else ""
            transcript_path = (
                os.path.join(transcript_output_dir, f"{title}.txt") if title else ""
            )

            if mp4_path and os.path.exists(mp4_path):
                if not (mp3_path and os.path.exists(mp3_path)):
                    try:
                        mp4_to_mp3(mp4_path, mp3_path)
                    except Exception as e:
                        print(f"Error converting {mp4_path} to MP3: {e}")

            if transcript_path and os.path.exists(transcript_path):
                try:
                    with open(transcript_path, "r", encoding="utf-8") as f:
                        transcript = f.read()
                    transcript_exists = True
                except Exception as e:
                    print(f"Error reading transcript for {video_id}: {e}")
            elif video_id:
                transcript = get_video_transcript(video_id)
                if transcript:
                    try:
                        with open(transcript_path, "w", encoding="utf-8") as f:
                            f.write(transcript)
                        transcript_exists = True
                    except Exception as e:
                        print(f"Error saving transcript for {video_id}: {e}")

            if transcript:
                transcript = sanitize_transcript(transcript)

            def is_qa_pairs_valid(qa_pairs_str: str) -> bool:
                try:
                    qa_pairs = json.loads(qa_pairs_str)
                    return (
                        isinstance(qa_pairs, list)
                        and len(qa_pairs) > 0
                        and all(
                            isinstance(q, dict) and "question" in q and "answer" in q
                            for q in qa_pairs
                        )
                    )
                except Exception:
                    return False

            qa_pairs_str = row.get("qa_pairs", "")
            needs_qa = not is_qa_pairs_valid(qa_pairs_str)
            qa_pairs = []
            if not needs_qa:
                try:
                    qa_pairs = json.loads(qa_pairs_str)
                except Exception:
                    qa_pairs = []
            elif transcript and transcript_exists:
                qa_pairs = generate_qa_pairs(transcript, num_pairs=5)

            dataset_rows.append(
                {
                    "url": url,
                    "video_id": video_id or "",
                    "title": title or "",
                    "mp4_path": mp4_path or "",
                    "mp3_path": mp3_path or "",
                    "transcript_path": transcript_path if transcript_exists else "",
                    "transcript_exists": transcript_exists,
                    "transcript": transcript if transcript_exists else "",
                    "qa_pairs": json.dumps(qa_pairs, ensure_ascii=False),
                }
            )

    return write_dataset_csv(dataset_rows, dataset_csv_path)


def main() -> None:
    """Entry point for the YouTube video processing pipeline."""
    os.makedirs(os.path.dirname(DATASET_CSV_PATH), exist_ok=True)
    result_csv_path = process_videos_from_csv(
        csv_path=VIDEOS_CSV_PATH,
        video_output_dir=OUTPUT_MP4_DIR,
        audio_output_dir=OUTPUT_MP3_DIR,
        transcript_output_dir=OUTPUT_TRANSCRIPTS_DIR,
        dataset_csv_path=DATASET_CSV_PATH,
    )
    print(f"Dataset CSV generated at: {result_csv_path}")


if __name__ == "__main__":
    main()
