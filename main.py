"""
Main orchestrator for the YouTube video processing pipeline.
This script coordinates downloading videos, converting to MP3, fetching transcripts, and writing the dataset CSV.
"""

import csv
import json
import os
from typing import Optional

from tqdm import tqdm

from src.converter import mp4_to_mp3
from src.dataset import write_dataset_csv
from src.downloader import download_video, get_video_id
from src.qa import generate_qa_pairs, sanitize_transcript
from src.transcript import get_video_transcript


def process_videos_from_csv(
    csv_path: str,
    video_output_dir: str,
    audio_output_dir: str,
    transcript_output_dir: str,
    dataset_csv_path: str,
) -> str:
    """
    Process a CSV file of YouTube URLs: download videos, convert to MP3, fetch transcripts, and write dataset CSV.
    Args:
        csv_path: Path to the input CSV file with YouTube URLs.
        video_output_dir: Directory to store downloaded MP4 files.
        audio_output_dir: Directory to store converted MP3 files.
        transcript_output_dir: Directory to store transcript text files.
        dataset_csv_path: Path to the output dataset CSV file.
    Returns:
        The path to the written dataset CSV file.
    """
    os.makedirs(video_output_dir, exist_ok=True)
    os.makedirs(audio_output_dir, exist_ok=True)
    os.makedirs(transcript_output_dir, exist_ok=True)
    dataset_rows = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))
        for row in tqdm(reader, desc="Processing videos", unit="video"):
            url = row.get("url")
            if not url:
                continue
            video_id: Optional[str] = get_video_id(url)
            title: Optional[str] = None
            mp4_path: Optional[str] = None
            mp3_path: Optional[str] = None
            transcript_path: Optional[str] = None
            transcript: Optional[str] = None
            transcript_exists: bool = False

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

            def is_qa_pairs_valid(qa_pairs_str):
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


if __name__ == "__main__":
    dataset_csv_path = "dataset/dataset.csv"
    os.makedirs(os.path.dirname(dataset_csv_path), exist_ok=True)
    result_csv_path = process_videos_from_csv(
        csv_path="videos.csv",
        video_output_dir="dataset/output_mp4",
        audio_output_dir="dataset/output_mp3",
        transcript_output_dir="dataset/output_transcripts",
        dataset_csv_path=dataset_csv_path,
    )
    print(f"Dataset CSV generated at: {result_csv_path}")
