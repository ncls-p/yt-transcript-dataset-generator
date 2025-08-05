"""Transcript sanitization and Q&A generation logic."""

import json
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


def sanitize_transcript(text: str) -> str:
    """
    Remove line breaks and excessive whitespace from transcript text.
    """
    if not text:
        return ""
    return " ".join(text.split())


def generate_qa_pairs(transcript: str, num_pairs: int = 5) -> List[Dict[str, str]]:
    """
    Generate question-answer pairs for a transcript using an OpenAI-compatible API.
    Reads model, API key, and API URL from environment variables.
    Returns a list of dicts: [{"question": ..., "answer": ...}, ...]
    """
    api_url = os.getenv("OPENAI_API_URL", "http://api.openai.com/v1/chat/completions")
    api_key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Skipping Q&A generation.")
        return []
    prompt = (
        f"Given the following transcript, generate {num_pairs} question-answer pairs that test comprehension. "
        "Return them as a JSON list of objects with 'question' and 'answer' fields.\nTranscript:\n"
        f"{transcript}"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates quiz questions.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        # Try to parse the JSON from the model's response
        try:
            qa_pairs = json.loads(content)
            if isinstance(qa_pairs, list):
                return qa_pairs
        except Exception:
            pass
        # Fallback: try to extract JSON from text
        import re

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            try:
                qa_pairs = json.loads(match.group(0))
                if isinstance(qa_pairs, list):
                    return qa_pairs
            except Exception:
                pass
        print("Failed to parse Q&A pairs from model response.")
        return []
    except Exception as e:
        print(f"Error generating Q&A pairs: {e}")
        return []
