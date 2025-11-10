import random
from typing import Dict, List
from spelling_bee_utils import is_correct_spelling


class SpellingBeeGame:
    """Core game logic for the Spelling Bee tournament."""

    def __init__(self, player_ids: List[str], word_list: List[str]):
        self.players: Dict[str, Dict] = {
            pid: {"score": 0, "is_active": True, "last_answer": None}
            for pid in player_ids
        }

        self.all_words = list(word_list)
        self.used_words = set()
        self.current_word = None

        self.CORRECT_SCORE = 10
        self.INCORRECT_PENALTY = -5
        self.WORDS_PER_TOURNAMENT = 10
        self.WORD_TIME_LIMIT_SECONDS = 15

        self.is_running = False

        print(f"Initialized with players: {', '.join(player_ids)}")

    # ------------------ Public API methods ------------------

    def start_game(self) -> str:
        """Starts the game and returns the first word."""
        if self.is_running:
            return self.current_word
        self.is_running = True
        return self.next_word()

    def next_word(self) -> str | None:
        """Advances to the next random word."""
        if not self.is_running:
            return None

        if len(self.used_words) >= self.WORDS_PER_TOURNAMENT:
            self.is_running = False
            return None

        available = list(set(self.all_words) - self.used_words)
        if not available:
            self.is_running = False
            return None

        self.current_word = random.choice(available)
        self.used_words.add(self.current_word)

        # Reset all players for the next round
        for pid in self.players:
            self.players[pid]["last_answer"] = None

        return self.current_word

    def process_answer(self, player_id: str, answer: str) -> tuple[bool, int]:
        """Processes an answer and updates score."""
        if not self.is_running or player_id not in self.players:
            return False, 0

        expected = self.current_word
        if not expected:
            return False, 0

        # Prevent duplicate submission
        if self.players[player_id]["last_answer"] == expected:
            return False, 0

        is_correct = is_correct_spelling(expected, answer)
        delta = self.CORRECT_SCORE if is_correct else self.INCORRECT_PENALTY
        self.players[player_id]["score"] += delta
        self.players[player_id]["last_answer"] = expected
        return is_correct, delta

    def get_scoreboard(self):
        """Returns the current scoreboard, sorted by score."""
        scoreboard = [
            {"player_id": pid, "score": data["score"]}
            for pid, data in self.players.items()
        ]

        return sorted(scoreboard, key=lambda x: x["score"], reverse=True)

    def send_word_to_players(self, current_word):
        """Sends the current word to active players."""
        # @TO-DO: Implement reliable multicast to send the word
        # start a timer
        for player_id in self.players:
            if self.players[player_id]["is_active"]:
                # Start timer
                # Send word to player
                # if reponse received:
                response = "GET_RESPONSE_WORD"
                self.process_answer(player_id, response)
                # else: disconnect player

    def player_connect(self, player_id: str):
        """Adds or reactivates a player."""
        if player_id not in self.players:
            self.players[player_id] = {
                "score": 0,
                "is_active": True,
                "last_answer": None,
            }
        else:
            self.players[player_id]["is_active"] = True

    def player_disconnect(self, player_id: str):
        """Marks a player as inactive."""
        if player_id in self.players:
            self.players[player_id]["is_active"] = False

    def disconnect_all_players(self):
        """Disconnects all players."""
        for pid in self.players:
            self.players[pid]["is_active"] = False

    def is_game_over(self) -> bool:
        """Checks if the game is finished."""
        return not self.is_running
