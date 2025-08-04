# yt-transcript-dataset-generator

A Python tool to automate the creation of datasets from YouTube videos, including downloading videos, converting them to MP3, fetching transcripts, and generating a structured CSV dataset.

## Features

- **Download YouTube videos** (supports standard and short URLs)
- **Convert MP4 videos to MP3 audio** using `moviepy`
- **Fetch video transcripts** (supports English and French, via `youtube-transcript-api`)
- **Generate a comprehensive CSV dataset** with video metadata, file paths, and transcript content
- **Clean, modular, and testable codebase** following Clean Architecture principles
- **Unit tests** for all core modules

## Project Structure

```
.
├── main.py                # Orchestrator: coordinates the workflow
├── videos.csv             # Input: list of YouTube URLs
├── src/
│   ├── downloader.py      # Download logic and video ID extraction
│   ├── converter.py       # MP4 to MP3 conversion
│   ├── transcript.py      # Transcript fetching
│   └── dataset.py         # Dataset CSV writing
├── tests/                 # Unit tests for each module
├── pyproject.toml         # Dependencies and project metadata
├── uv.lock                # Lock file for dependencies (if using uv)
└── README.md
```

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/ncls-p/yt-transcript-dataset-generator.git
   cd yt-transcript-dataset-generator
   ```

2. **Install Python 3.13+**

3. **Set up your environment and install dependencies:**

   **With [uv](https://github.com/astral-sh/uv) (recommended):**

   ```sh
   # Create and sync the environment (installs all dependencies, including dev)
   uv sync
   # To run your code in the uv-managed environment:
   uv run python main.py
   ```

   **To generate `requirements.txt` from your lockfile (for pip compatibility):**

   ```sh
   uv export --no-emit-workspace --no-dev --no-annotate --no-header --no-hashes --output-file requirements.txt
   # or
   uv pip compile --all-extras --output-file requirements.txt
   ```

   **Without uv (using a standard Python virtual environment):**

   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install .
   # or
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare your input:**

   - Add YouTube URLs to `videos.csv` (one per line, with a header `url`).

2. **Run the main script:**

   ```sh
   python main.py
   ```

3. **Output:**
   - Downloaded MP4s: `dataset/output_mp4/`
   - Converted MP3s: `dataset/output_mp3/`
   - Transcripts: `dataset/output_transcripts/`
   - Final dataset CSV: `dataset/dataset.csv`

## Dataset Folder Structure

The `dataset/` folder contains:

- `output_mp4/`: Downloaded MP4 video files
- `output_mp3/`: Converted MP3 audio files
- `output_transcripts/`: Transcript text files
- `dataset.csv`: Final dataset CSV file

## Dataset CSV Format

Each row contains:

- `url`: YouTube video URL
- `video_id`: Extracted video ID
- `title`: Video title (from filename)
- `mp4_path`: Path to downloaded MP4
- `mp3_path`: Path to converted MP3
- `transcript_path`: Path to transcript file (if available)
- `transcript_exists`: Boolean flag
- `transcript`: Transcript text (if available)

## Architecture & Design

- **Orchestrator (`main.py`)**: Coordinates the workflow (download, convert, transcribe, write CSV)
- **Domain Services**: Each module in `src/` has a single responsibility
- **Testability**: All logic is modular and covered by unit tests in `tests/`
- **Extensibility**: Add new features by creating new modules in `src/` and updating `main.py`

## Testing

Run all tests with:

```sh
pytest
```

## Dependencies

- `moviepy` (video/audio conversion)
- `yt-dlp` (YouTube downloading)
- `youtube-transcript-api` (transcript fetching)
- `pytest` (testing)

## Contributing

1. Fork the repo and create your branch.
2. Add tests for new features.
3. Follow Clean Code and Clean Architecture principles.
4. Submit a pull request.
