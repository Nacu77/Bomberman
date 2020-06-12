from src.Game import Game


"""-----------Minimax Algorithm-----------"""


def min_max(state):
    if state.depth == 0 or state.game.final():
        state.score = state.game.estimate_score(state.depth)
        return state

    state.possible_moves = state.state_moves()
    moves_score = [min_max(move) for move in state.possible_moves]

    if state.current_player_symbol == Game.MAX_PLAYER:
        state.chosen_state = max(moves_score, key=lambda x: x.score)
    else:
        state.chosen_state = min(moves_score, key=lambda x: x.score)

    state.score = state.chosen_state.score
    return state


"""-----------Alpha-Beta Algorithm-----------"""


def alpha_beta(alpha, beta, state):
    if state.depth == 0 or state.game.final():
        state.score = state.game.estimate_score(state.depth)
        return state

    if alpha >= beta:
        return state

    state.possible_moves = state.state_moves()

    if state.current_player_symbol == Game.MAX_PLAYER:
        current_score = float("-inf")
        for move in state.possible_moves:
            new_state = alpha_beta(alpha, beta, move)
            if current_score < new_state.score:
                state.chosen_state = new_state
                current_score = new_state.score
            if alpha < new_state.score:
                alpha = new_state.score
                if alpha >= beta:
                    break

    elif state.current_player_symbol == Game.MIN_PLAYER:
        current_score = float("inf")
        for move in state.possible_moves:
            new_state = alpha_beta(alpha, beta, move)
            if current_score > new_state.score:
                state.chosen_state = new_state
                current_score = new_state.score
            if beta > new_state.score:
                beta = new_state.score
                if alpha >= beta:
                    break

    state.score = state.chosen_state.score
    return state
