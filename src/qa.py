"""Transcript sanitization and Q&A generation logic."""

import json
import os
import re
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def generate_qa_pairs(transcript: str, num_pairs: int = 5) -> List[Dict[str, str]]:
    """
    Generate question-answer pairs for a transcript using the OpenAI Python client.
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

    client = OpenAI(
        api_key=api_key, base_url=api_url.replace("/v1/chat/completions", "")
    )

    try:
        from openai.types.chat import (
            ChatCompletionSystemMessageParam,
            ChatCompletionUserMessageParam,
        )

        messages = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="You are a helpful assistant that creates quiz questions.",
            ),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        content = completion.choices[0].message.content
        if not content:
            print("No content returned from model.")
            return []
        try:
            qa_pairs = json.loads(content)
            if isinstance(qa_pairs, list):
                for q in qa_pairs:
                    if not (isinstance(q, dict) and "question" in q and "answer" in q):
                        raise ValueError("Malformed Q&A object")
                return qa_pairs
        except Exception:
            pass

        match = re.search(r"\[.*\]", content, re.DOTALL) if content else None
        if match:
            try:
                qa_pairs = json.loads(match.group(0))
                if isinstance(qa_pairs, list):
                    for q in qa_pairs:
                        if not (
                            isinstance(q, dict) and "question" in q and "answer" in q
                        ):
                            raise ValueError("Malformed Q&A object")
                    return qa_pairs
            except Exception:
                pass
        print("Failed to parse Q&A pairs from model response.")
        return []
    except Exception as e:
        print(f"Error generating Q&A pairs: {e}")
        return []
