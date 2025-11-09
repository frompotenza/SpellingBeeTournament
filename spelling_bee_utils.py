import csv
import io
from typing import List

# --- Word Loading Configuration and Logic ---

# Define the expected path to the word list CSV file.
WORD_FILEPATH = "./words.csv"


def load_words_from_csv():
    """
    Loads a list of words from a CSV file, expecting one word per row
    in the first column (after the header).

    Args:
        filepath: The path to the CSV file.

    Returns:
        A list of cleaned, non-empty words.
    """
    words = []
    print(f"Attempting to load words from: {WORD_FILEPATH}")

    try:
        reader = csv.reader(WORD_FILEPATH)

        for row in reader:
            if row:
                word = row[0].strip().lower()
                if word:
                    words.append(word)
    except Exception as e:
        print(f"An error occurred while parsing the CSV: {e}. Returning empty list.")
        return []

    print(f"Successfully loaded {len(words)} words.")
    return words


def is_correct_spelling(expected_word, player_answer):
    """
    A simple validation function that checks if the player's answer
    matches the expected word (case and whitespace insensitive).
    """
    return expected_word.lower() == player_answer.strip().lower()


def get_connected_players():
    """Returns list of players connected"""
    # @TO-DO
    players = ["Felipe", "Mirabell", "Federico"]
    return players
