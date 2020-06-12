import time
from src.Game import Game, Player, Bomb, in_explosion_range
from src.State import State
from src.Algorithms import min_max, alpha_beta


def print_if_final(current_state):
    """
    Print the winner or "draw" if the game is over
    :param current_state: object of type State
    :return: True if the game is over, or False
    """
    final = current_state.game.final()
    if final:
        if final == "draw":
            print("Draw!")
        elif final == Game.MIN_PLAYER:
            print("You won!")
        else:
            print("you lost...")
        print(f"Your score is: {current_state.game.score(Game.MIN_PLAYER)}")
        print(f"PC's score is: {current_state.game.score(Game.MAX_PLAYER)}")
        return True
    return False


def update_current_state(current_state):
    """
    Update the current_state with the input that the player choose
    :param current_state: object of type State
    :return: True if the game will continue, False if the player choose to quit
    """
    old_position = current_state.game.player_min.position
    new_position = None

    # Ask the player in which direction he wants to go
    valid_answer = False
    while not valid_answer:
        direction = input("Choose the direction you want to go or write 'exit' if you want to quit. (w for up, s for down, a for left, d for right)\n")
        if direction == 'exit':
            return False
        if direction in ["w", "s", "a", "d"]:
            if direction == "w":
                if current_state.game.the_map[old_position[0] - 1][old_position[1]] not in ["#", "b"]:
                    valid_answer = True
                    new_position = (old_position[0] - 1, old_position[1])
                else:
                    print("There is a wall or a bomb there, please choose another direction\n")
            elif direction == "s":
                if current_state.game.the_map[old_position[0] + 1][old_position[1]] not in ["#", "b"]:
                    valid_answer = True
                    new_position = (old_position[0] + 1, old_position[1])
                else:
                    print("There is a wall or a bomb there, please choose another direction\n")
            elif direction == "a":
                if current_state.game.the_map[old_position[0]][old_position[1] - 1] not in ["#", "b"]:
                    valid_answer = True
                    new_position = (old_position[0], old_position[1] - 1)
                else:
                    print("There is a wall or a bomb there, please choose another direction\n")
            else:
                if current_state.game.the_map[old_position[0]][old_position[1] + 1] not in ["#", "b"]:
                    valid_answer = True
                    new_position = (old_position[0], old_position[1] + 1)
                else:
                    print("There is a wall or a bomb there, please choose another direction\n")
        else:
            print("Please enter w, s, a or d\n")

    # Update the map
    current_state.game.the_map[old_position[0]][old_position[1]] = " "
    # Check if in the new position is a protection
    if current_state.game.the_map[new_position[0]][new_position[1]] == 'p':
        current_state.game.player_min.protection += 1
    current_state.game.the_map[new_position[0]][new_position[1]] = Game.MIN_PLAYER
    current_state.game.player_min.position = new_position

    # Check if the new position is in the range of an explosion (updates the protection and remove some bombs if necessary)
    check_explosion(current_state, current_state.game.player_min)

    # If the player didn't have any bomb, ask him if he wants to place one behind him
    if current_state.game.player_min.bomb is None:
        valid_answer = False
        while not valid_answer:
            answer = input("Do you want to place an inactive bomb behind you? Answer with y/n\n")
            if answer in ['y', 'n']:
                if answer == 'y':
                    current_state.game.the_map[old_position[0]][old_position[1]] = "b"
                    current_state.game.player_min.bomb = Bomb("inactive", old_position)
                valid_answer = True
            else:
                print("You didn't choose the correct answer...\n")

    # If the player has an inactive bomb placed on the map, ask him if he wants to activate it
    elif current_state.game.player_min.bomb.status == "inactive":
        valid_answer = False
        while not valid_answer:
            answer = input("Do you want to activate the bomb? Answer with y/n\n")
            if answer in ['y', 'n']:
                if answer == 'y':
                    current_state.game.player_min.bomb.status = "active"
                valid_answer = True
            else:
                print("You didn't choose the correct answer...\n")

    # If the player has an active bomb placed on the map, ask him if he wants to explode it and place another one behind him
    else:
        valid_answer = False
        while not valid_answer:
            answer = input("Do you want to place an inactive bomb behind you (the bomb you already have will explode)? Answer with y/n\n")
            if answer in ['y', 'n']:
                if answer == 'y':
                    current_state.game.the_map[current_state.game.player_min.bomb.position[0]][current_state.game.player_min.bomb.position[1]] = " "
                    current_state.game.the_map[old_position[0]][old_position[1]] = "b"
                    current_state.game.player_min.bomb = Bomb("inactive", old_position)
                valid_answer = True
            else:
                print("You didn't choose the correct answer...\n")

    return True


def initialize_game(path):
    """
    :param path: string, representing the path of the file where the map is stored
    :return: object of type Game, representing the intial Game
    """
    with open(path, "r") as f:
        lines = f.readlines()
        the_map = [[c for c in line if c != "\n"] for line in lines]

    player_min = None
    player_max = None
    for i in range(len(the_map)):
        for j in range(len(the_map[i])):
            if the_map[i][j] == Game.MIN_PLAYER:
                player_min = Player(0, (i, j), None)
            elif the_map[i][j] == Game.MAX_PLAYER:
                player_max = Player(0, (i, j), None)

    return Game(player_min, player_max, the_map)


def check_explosion(current_state, player):
    """
    Check if the "player" is in the range of an explosion, if yes decrease his protection and explode the bomb
    :param current_state: object of type State, representing the current state
    :param player: object of type Player, representing the player checked for the explosion
    """
    explosion = in_explosion_range(current_state.game, player.position)
    if explosion[0]:
        player.protection -= 1
        if current_state.game.player_min.bomb and explosion[1] == current_state.game.player_min.bomb.position:
            current_state.game.player_min.bomb = None
        else:
            current_state.game.player_max.bomb = None
        current_state.game.the_map[explosion[1][0]][explosion[1][1]] = " "


def main():
    """
    Here's where the magic happens
    """

    # Ask what algorithm to use (Minimax or Alpha-Beta)
    algorithm_type = None
    valid_answer = False
    while not valid_answer:
        algorithm_type = input("What algorithm do you wanna use? Minimax(1) or Alpha-Beta(2)\n")
        if algorithm_type in ['1', '2']:
            valid_answer = True
        else:
            print("You didn't choose the correct answer...\n")

    # Ask the difficulty of the game
    valid_answer = False
    while not valid_answer:
        difficulty = input("Choose difficulty: hard / medium / easy\n")
        if difficulty == "hard":
            State.DEPTH_MAX = 9
            valid_answer = True
        elif difficulty == "medium":
            State.DEPTH_MAX = 6
            valid_answer = True
        elif difficulty == "easy":
            State.DEPTH_MAX = 3
            valid_answer = True
        else:
            print("You didn't choose the correct answer...\n")

    # Ask if he wants to be the first or the second
    valid_answer = False
    while not valid_answer:
        Game.MIN_PLAYER = input("Do you wanna be the first or the second player? Answer with 1 or 2\n")
        if Game.MIN_PLAYER in ['1', '2']:
            valid_answer = True
        else:
            print("You didn't choose the correct answer...\n")
    Game.MAX_PLAYER = '1' if Game.MIN_PLAYER == '2' else '2'

    print("Game starting...")

    # Creating the initial state
    game = initialize_game("map.txt")
    print(str(game))
    current_state = State(game, '1', State.DEPTH_MAX)

    min_player_moves = 0
    max_player_moves = 0

    while True:
        # at the start of any turn, check if any of the players are in the range of the explosion (and update the attributes)
        check_explosion(current_state, current_state.game.player_min)
        check_explosion(current_state, current_state.game.player_max)

        # Player's turn
        if current_state.current_player_symbol == Game.MIN_PLAYER:
            time_start = time.time()

            if update_current_state(current_state) is False:
                print("You quit the game...")
                print(f"Your score is: {current_state.game.score(Game.MIN_PLAYER)}")
                print(f"PC's score is: {current_state.game.score(Game.MAX_PLAYER)}")
                break
            print("After your move:\n")
            print(str(current_state.game))

            time_stop = time.time()
            print(f"It took {time_stop - time_start} for the player to make the move\n")
            if print_if_final(current_state):
                break
            current_state.current_player_symbol = current_state.opossite_player()
            min_player_moves += 1

        # PC's turn
        else:
            time_start = time.time()

            if algorithm_type == '1':
                updated_state = min_max(current_state)
            else:
                updated_state = alpha_beta(-500, 500, current_state)
            current_state.game = updated_state.chosen_state.game
            print("After pc's move:\n")
            print(str(current_state.game))

            time_stop = time.time()
            print(f"It took {time_stop - time_start} for the pc to make the move\n")
            if print_if_final(current_state):
                break
            current_state.current_player_symbol = current_state.opossite_player()
            max_player_moves += 1

    print(f"You made {min_player_moves} moves; The PC made {max_player_moves} moves.")


if __name__ == '__main__':
    total_time_start = time.time()
    main()
    total_time_stop = time.time()
    print(f"The game was running for {total_time_stop - total_time_start}")
