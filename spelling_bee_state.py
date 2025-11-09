import random
from typing import Dict
from spelling_bee_utils import *


class SpellingBeeGame:
    """
    Manages the core functional state and logic of the Spelling Bee Tournament.
    This class is intended to run on the elected Leader peer.
    """

    def __init__(self, player_ids, word_list):
        """
        Initializes the game state.

        Args:
            player_ids: A list of unique identifiers for all players in the session.
            word_list: The list of words to be used in the tournament.
        """
        self.all_words = list(word_list)
        random.shuffle(self.all_words)
        self.num_players = len(player_ids)
        self.players: Dict[str, Dict] = {}

        for pid in player_ids:
            # Store player state: score, and active status (for fail-stop handling)
            self.players[pid] = {"score": 0, "is_active": True, "last_answer": None}

        self.CORRECT_SCORE = 10
        self.INCORRECT_PENALTY = -5
        self.WORDS_PER_TOURNAMENT = 10
        self.WORD_TIME_LIMIT_SECONDS = 15

        self.current_word_index = -1
        self.is_running = False
        print(
            f"Game initialized with {self.num_players} players: {', '.join(player_ids)}"
        )

    def start_game(self):
        """
        Starts the tournament and advances to the first word.
        Returns the first word to be broadcast.
        """
        if self.is_running:
            return self.get_current_word()

        self.is_running = True
        print("--- Tournament Started ---")
        return self.next_round()

    def get_current_word(self):
        """Returns the word for the current round."""
        if (
            self.current_word_index < 0
            or self.current_word_index >= self.WORDS_PER_TOURNAMENT
        ):
            return None
        return self.all_words[self.current_word_index]

    def _get_active_player_count(self) -> int:
        """Helper method to count how many players are still active."""
        return sum(1 for data in self.players.values() if data["is_active"])

    def process_answer(self, player_id, answer):
        """
        Validates a player's spelling and updates their score.

        Args:
            player_id: The ID of the player submitting the answer.
            answer: The word they submitted.

        Returns:
            A tuple (is_correct, score_change)
        """
        if not self.is_running or player_id not in self.players:
            return False, 0

        expected_word = self.get_current_word()
        if not expected_word:
            print(f"Error: Attempted to process answer when game is over or stopped.")
            return False, 0

        # Check if the player has already submitted an answer for this round
        if self.players[player_id]["last_answer"] == expected_word:
            print(f"Player {player_id} attempted to submit twice for {expected_word}.")
            return False, 0  # No score change, already submitted

        is_correct = is_correct_spelling(expected_word, answer)
        score_change = 0

        if is_correct:
            score_change = self.CORRECT_SCORE
        else:
            score_change = self.INCORRECT_PENALTY

        self.players[player_id]["score"] += score_change
        self.players[player_id][
            "last_answer"
        ] = expected_word  # Mark as having submitted

        # Log the result for the Leader to broadcast
        print(
            f"Answer from {player_id}: '{answer}' -> {'CORRECT' if is_correct else 'INCORRECT'} ({score_change} pts)"
        )

        return is_correct, score_change

    def send_word_to_players(self, current_word):
        # start a timer
        for player_id in self.players:
            if self.players[player_id]["is_active"]:
                # Start timer
                # Send word to player
                # if reponse received:
                response = "GET_RESPONSE_WORD"
                self.process_answer(player_id, response)
                # else: disconnect player

    def next_round(self):
        """
        Moves the game state to the next word/round.

        Returns:
            The next word if the game continues, or None if the game is over.
        """
        if not self.is_running:
            return None

        active_players = self._get_active_player_count()
        if active_players <= 1:
            self.is_running = False
            print(f"--- Game Over: Only {active_players} player(s) remaining. ---")
            return None

        if self.current_word_index >= self.WORDS_PER_TOURNAMENT - 1:
            self.is_running = False
            print(
                f"--- Game Over: {self.WORDS_PER_TOURNAMENT} words have been used. ---"
            )
            return None

        self.current_word_index += 1

        next_word = self.get_current_word()
        print(f"\n--- Starting Round {self.current_word_index + 1} ---")
        print(f"New word to broadcast: '{next_word}'")

        # Reset 'last_answer' tracker for all active players
        for player_id in self.players:
            if self.players[player_id]["is_active"]:
                self.players[player_id]["last_answer"] = None

        return next_word

    def player_disconnect(self, player_id):
        """
        Handles a fail-stop event by marking a player as inactive.
        The leader continues the game with the remaining active peers.
        """
        if player_id in self.players:
            self.players[player_id]["is_active"] = False
            print(
                f"Player {player_id} has disconnected/crashed (Fail-Stop). Marked as inactive."
            )

    def disconnect_all_players(self):
        for player_id in self.players:
            self.player_disconnect(player_id)

    def get_scoreboard(self):
        """
        Returns the current scoreboard, sorted by score.
        """
        # Convert the dictionary to a list of score objects
        scoreboard = [
            {"player_id": pid, "score": data["score"], "is_active": data["is_active"]}
            for pid, data in self.players.items()
        ]
        # Sort by score in descending order
        scoreboard.sort(key=lambda x: x["score"], reverse=True)
        return scoreboard


# --- Example Usage (Demonstrates how a Leader would use this class) ---
if __name__ == "__main__":
    # 0. Load the words from the mock CSV content
    word_list = load_words_from_csv()

    # 1. Simulate players joining the session
    initial_players = get_connected_players()
    game = SpellingBeeGame(initial_players, word_list)

    # 2. Start the game (The Leader sends this word via reliable multicast)
    current_word = game.start_game()

    while game.is_running:
        game.send_word_to_players(current_word)

        print("\n--- Current Scoreboard After Round 1 ---")
        for entry in game.get_scoreboard():
            print(
                f"{entry['player_id']}: {entry['score']} points (Active: {entry['is_active']})"
            )

        # 5. Advance to the next round
        next_word = game.next_round()

    print("\n--- Final Scoreboard ---")
    for entry in game.get_scoreboard():
        print(
            f"{entry['player_id']}: {entry['score']} points (Active: {entry['is_active']})"
        )

    game.disconnect_all_players()
