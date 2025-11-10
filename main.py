from spelling_bee_utils import load_words_from_csv, get_connected_players
from spelling_bee_logic import SpellingBeeGame


def main():
    # Load words
    word_list = load_words_from_csv()
    if not word_list:
        print("No words available. Exiting.")
        return

    # Connect players
    initial_players = get_connected_players()
    if not initial_players:
        print("No players connected. Exiting.")
        return

    # Initialize game
    game = SpellingBeeGame(initial_players, word_list)
    current_word = game.start_game()

    while not game.is_game_over():
        print(f"\n--- New Word: '{current_word}' ---")
        game.send_word_to_players(current_word)

        # Show scoreboard
        print("\n--- Scoreboard ---")
        for entry in game.get_scoreboard():
            if entry["is_active"]:
                print(f"{entry['player_id']}: {entry['score']} pts")

        current_word = game.next_word()

    print("\n--- Final Scoreboard ---")
    for entry in game.get_scoreboard():
        if entry["is_active"]:
            print(f"{entry['player_id']}: {entry['score']} pts")

    game.disconnect_all_players()


if __name__ == "__main__":
    main()
