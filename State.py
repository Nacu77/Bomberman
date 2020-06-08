"""
    Nume: Nacu Florin Ionut
    grupa: 242
"""

from Proiect_Pb2.Game import Game


class State:
    DEPTH_MAX = None   # the max depth of the tree which actually represents the dificulty of the game

    def __init__(self, game, current_player_symbol, depth, score=None):
        """
        :param game: object of type Game
        :param current_player_symbol: "MIN_PLAYER" or "MAX_PLAYER"
        :param depth: the current depth
        :param score: the score
        """
        self.game = game
        self.current_player_symbol = current_player_symbol
        self.depth = depth
        self.score = score
        self.possible_moves = []
        self.chosen_state = None

    def opossite_player(self):
        """
        :return: the symbol of the player who's moving on the next turn
        """
        if self.current_player_symbol == Game.MIN_PLAYER:
            return Game.MAX_PLAYER
        else:
            return Game.MIN_PLAYER

    def state_moves(self):
        """
        :return: a list of State objects, representing all the possible moves for the current player
        """
        moves_list = self.game.game_moves(self.current_player_symbol)
        opossite_player = self.opossite_player()

        state_moves_list = [State(move, opossite_player, self.depth - 1) for move in moves_list]
        return state_moves_list
