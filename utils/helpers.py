"""
Utility functions for HiveEngine.
"""

import hashlib
import json
from pathlib import Path
from typing import Any


def calculate_hash(content: str) -> str:
    """Calculate SHA-256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()


def load_json(file_path: str) -> Any:
    """Load JSON from file."""
    with open(file_path) as f:
        return json.load(f)


def save_json(data: Any, file_path: str):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def format_tokens(tokens: int) -> str:
    """Format token count as human-readable string."""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    return str(tokens)


def format_cost(cost: float) -> str:
    """Format cost as USD string."""
    return f"${cost:.2f}"


def get_file_extension(filename: str) -> str:
    """Get file extension."""
    return Path(filename).suffix.lower()


def is_code_file(filename: str) -> bool:
    """Check if file is a code file."""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
        '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift',
        '.kt', '.scala', '.r', '.m', '.mm', '.pl', '.sh', '.bash'
    }
    return get_file_extension(filename) in code_extensions
