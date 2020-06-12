class Game:
    MIN_PLAYER = None   # the symbol of the player
    MAX_PLAYER = None   # the symbol of the pc

    def __init__(self, player_min, player_max, the_map):
        """
        :param player_min: object of type Player, representing the player
        :param player_max: object of type Player, representing the pc
        :param the_map: matrix of chars, representing the map
        """
        self.player_min = player_min
        self.player_max = player_max
        self.the_map = the_map

    def final(self):
        """
        When the protection of a player reaches -1, the game is over.
        :return: the symbol of the player who won the game, or "draw" if it's a draw, or False if the game isn't finished
        """
        if self.player_min.protection == self.player_max.protection == -1:
            return "draw"
        if self.player_min.protection == -1:
            return Game.MAX_PLAYER
        if self.player_max.protection == -1:
            return Game.MIN_PLAYER
        return False

    def game_moves(self, player_symbol):
        """
        :param player_symbol: "MIN_PLAYER" or "MAX_PLAYER", representing the symbol of the player who makes the move
        :return: a list of Game objects, representing all the possible moves that the player with the symbol "player_symbol" can make for the next turn
        """
        moves_list = []

        # ---------------MIN_PLAYER---------------
        if player_symbol == Game.MIN_PLAYER:
            i = self.player_min.position[0]
            j = self.player_min.position[1]

            # for every direction (right, left, down, up)
            for p, q in [(i, j + 1), (i, j - 1), (i + 1, j), (i - 1, j)]:
                # verifies if it's a valid move (there are no obstacles there)
                if self.the_map[p][q] in [" ", "p"]:
                    new_map = [line.copy() for line in self.the_map]
                    new_map[i][j] = " "
                    new_map[p][q] = player_symbol
                    x = 0

                    # increase the number of protections if the player falls on a protecion
                    if self.the_map == "p":
                        x += 1

                    # decrease the number of protections if the player gets on a explosion range and also erase the bomb (because it exploded)
                    # also initialize the new players
                    explosion = in_explosion_range(self, self.player_min.position)
                    if explosion[0]:
                        x -= 1
                        if self.player_min.bomb and explosion[1] == self.player_min.bomb.position:  # if it's the player's bomb
                            new_player_min = Player(self.player_min.protection + x, (p, q), None)
                            new_player_max = self.player_max
                        else:   # if it's the pc's bomb
                            new_player_min = Player(self.player_min.protection + x, (p, q), self.player_min.bomb)
                            new_player_max = Player(self.player_max.protection, self.player_max.position, None)
                        new_map[explosion[1][0]][explosion[1][1]] = " "
                    else:
                        new_player_min = Player(self.player_min.protection + x, (p, q), self.player_min.bomb)
                        new_player_max = self.player_max

                    moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))  # in this move the player just changed the position (up/down/left/right)
                    if self.player_min.bomb:
                        if self.player_min.bomb.status == "inactive":
                            new_player_min = Player(self.player_min.protection + x, (p, q), Bomb("active", self.player_min.bomb.position))
                            moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))  # in this move the player also activated a bomb that he placed in the past
                        new_map[self.player_min.bomb.position[0]][self.player_min.bomb.position[1]] = " "
                        new_player_min = Player(self.player_min.protection + x, (p, q), Bomb("inactive", (i, j)))
                        new_map[i][j] = "b"
                        moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))  # in this move the player erased the bomb from the old position and placed a new one behind him
                    else:
                        new_player_min = Player(self.player_min.protection + x, (p, q), Bomb("inactive", (i, j)))
                        new_map[i][j] = "b"
                        moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))  # in this move the player didn't have any other bomb placed on the map, and he placed a new one behind him

        # ---------------MAX_PLAYER---------------
        else:
            i = self.player_max.position[0]
            j = self.player_max.position[1]
            for p, q in [(i, j + 1), (i, j - 1), (i + 1, j), (i - 1, j)]:
                if self.the_map[p][q] in [" ", "p"]:
                    new_map = [line.copy() for line in self.the_map]
                    new_map[i][j] = " "
                    new_map[p][q] = player_symbol

                    x = 0
                    if self.the_map == "p":
                        x += 1

                    explosion = in_explosion_range(self, self.player_max.position)
                    if explosion[0]:
                        x -= 1
                        if self.player_min.bomb and explosion[1] == self.player_min.bomb.position:
                            new_player_min = Player(self.player_min.protection, self.player_min.position, None)
                            new_player_max = Player(self.player_max.protection + x, (p, q), self.player_max.bomb)
                        else:
                            new_player_min = self.player_min
                            new_player_max = Player(self.player_max.protection + x, (p, q), None)
                        new_map[explosion[1][0]][explosion[1][1]] = " "
                    else:
                        new_player_min = self.player_min
                        new_player_max = Player(self.player_max.protection + x, (p, q), self.player_max.bomb)

                    moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))
                    if self.player_max.bomb:
                        if self.player_max.bomb.status == "inactive":
                            new_player_max = Player(self.player_max.protection + x, (p, q), Bomb("active", self.player_max.bomb.position))
                            moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))
                        new_map[self.player_max.bomb.position[0]][self.player_max.bomb.position[1]] = " "
                        new_player_max = Player(self.player_max.protection + x, (p, q), Bomb("inactive", (i, j)))
                        new_map[i][j] = "b"
                        moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))
                    else:
                        new_player_max = Player(self.player_max.protection + x, (p, q), Bomb("inactive", (i, j)))
                        new_map[i][j] = "b"
                        moves_list.append(Game(new_player_min, new_player_max, [line.copy() for line in new_map]))

        # in case the player can't move in any direction
        if len(moves_list) == 0:
            moves_list.append(self)

        return moves_list

    def score(self, player_symbol):
        """
        :param player_symbol: "MIN_PLAYER" or "MAX_PLAYER", representing the symbol of the player for who the score is calculated
        :return: int, representing the score
        """
        if player_symbol == Game.MIN_PLAYER:
            current_player = self.player_min
            opossite_player = self.player_max
        else:
            current_player = self.player_max
            opossite_player = self.player_min

        s = 0
        if current_player.bomb:
            if current_player.bomb.status == 'active':
                s += 50
            else:
                s += 25
            s -= min((abs(opossite_player.position[0] - current_player.bomb.position[0]), abs(opossite_player.position[1] - current_player.bomb.position[1])))
        s += 25 * self.player_min.protection
        return s

    def estimate_score(self, depth):
        """
        :param depth: the depth of the current game in the tree
        :return: int, representing a score
        """
        test_final = self.final()
        if test_final == Game.MAX_PLAYER:
            return 999 + depth
        if test_final == Game.MIN_PLAYER:
            return -999 - depth
        if test_final == "draw":
            return 0
        return self.score(Game.MAX_PLAYER) - self.score(Game.MIN_PLAYER)

    def __str__(self):
        str_map = ""
        for i in range(len(self.the_map)):
            str_map += "".join(self.the_map[i]) + "\n"

        str_messages = f"You have {self.player_min.protection} protections.\n"
        if self.player_min.bomb is None:
            str_messages += f"You didn't place any bomb.\n"
        else:
            str_messages += f"You have an {self.player_min.bomb.status} bomb placed at {self.player_min.bomb.position}.\n"

        str_messages += f"The PC has {self.player_max.protection} protections.\n"
        if self.player_max.bomb is None:
            str_messages += f"The PC didn't place any bomb.\n"
        else:
            str_messages += f"The PC has an {self.player_max.bomb.status} bomb placed at {self.player_max.bomb.position}.\n"

        return str_map + str_messages


class Bomb:
    def __init__(self, status, position):
        """
        :param status: "active" or "inactive", which means if the bomb is active or not
        :param position: a tuple, representing the position of the bomb on the map
        """
        self.status = status
        self.position = position


class Player:
    def __init__(self, protection, position, bomb):
        """
        :param protection: the number of protection that the player has
        :param position: the position of the player on the map
        :param bomb: object of type Bomb, representing the bomb that the player have placed, or None if he didn't place any bomb
        """
        self.protection = protection
        self.position = position
        self.bomb = bomb


def in_explosion_range(game, player_position):
    """
    :param game: object of type Game, representing the current game
    :param player_position: a tuple, representing the position of the player on the map
    :return: a list of two elements, the first element is True if the player is in the explosion range, the second element is the position of the bomb who hit the player
    """
    the_map = game.the_map

    # verifies for both bombs
    for bomb in [game.player_min.bomb, game.player_max.bomb]:
        if bomb:
            if bomb.status == "active":
                bomb_position = bomb.position

                # when explosion extends down
                i = bomb_position[0] + 1
                while the_map[i][bomb_position[1]] not in ["#", "b"]:
                    if player_position == (i, bomb_position[1]):
                        return [True, bomb_position]
                    i += 1

                # when explosion extends up
                i = bomb_position[0] - 1
                while the_map[i][bomb_position[1]] not in ["#", "b"]:
                    if player_position == (i, bomb_position[1]):
                        return [True, bomb_position]
                    i -= 1

                # when explosion extends right
                j = bomb_position[1] + 1
                while the_map[bomb_position[0]][j] not in ["#", "b"]:
                    if player_position == (bomb_position[0], j):
                        return [True, bomb_position]
                    j += 1

                # when explosion extends left
                j = bomb_position[1] - 1
                while the_map[bomb_position[0]][j] not in ["#", "b"]:
                    if player_position == (bomb_position[0], j):
                        return [True, bomb_position]
                    j -= 1

    return [False, None]
