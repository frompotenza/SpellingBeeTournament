import csv
import os
from typing import List


def load_words_from_csv(file_path: str = "words.csv") -> List[str]:
    """Load words from a CSV file (one word per line)."""
    if not os.path.exists(file_path):
        print(f"CSV file not found: {file_path}")
        return []

    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        # Read the first row only
        row = next(reader, [])
        # Strip spaces from each word
        words = [word.strip() for word in row if word.strip()]
    return words


def is_correct_spelling(expected: str, answer: str) -> bool:
    """Check if the player's answer is correct (case-insensitive)."""
    return expected.lower() == answer.strip().lower()


def get_connected_players():
    """Returns list of players connected"""
    # @TO-DO
    players = ["Felipe", "Mirabell", "Federico"]
    return players
