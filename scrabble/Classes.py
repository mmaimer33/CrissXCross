import enum
from random import shuffle
import numpy

from scrabble.Values import *

class Tile:
    """Represents a tile. Contains a letter and a score based on the global LETTER_SCORES."""

    def __init__(self, letter: str) -> None:
        self.letter = letter
        self.score = LETTER_SCORES[letter]
        
    def __eq__(self, __o: object) -> bool:
        if __o is self:
            return True
        if isinstance(__o, Tile):
            return __o.get_letter() == self.get_letter()
        return False
        
    def get_letter(self):
        return self.letter
    
    def get_score(self):
        return self.score

class Bag:
    """Represents a bag. Filled with standard 100 tiles and shuffled when initialized."""

    def __init__(self) -> None:
        self.bag = []
        self.initialize_bag()
    
    # Adds a given tile to the bag a given quantity times.
    def add_to_bag(self, tile: Tile, quantity: int):
        for i in range(quantity):
            self.bag.append(tile)
    
    # Adds standard 100 tiles to bag using LETTER_COUNTS and shuffles the bag.
    def initialize_bag(self):
        for letter in LETTER_COUNTS.keys():
            self.add_to_bag(Tile(letter), LETTER_COUNTS[letter])
        shuffle(self.bag)
    
    # Removes a tile from the bag and returns it.
    def extract_tile(self):
        return self.bag.pop()
    
    # Returns the number of tiles remaining in the bad.
    def get_remaining_tiles(self):
        return len(self.bag)

class Rack:
    """Represents a player's rack / hand. Can hold upto 7 tiles and is refilled if some are used,
        as long as the bag has tiles."""
    
    def __init__(self, bag: Bag) -> None:
        self.rack = []
        self.bag = bag
        self.replenish_rack()
    
    # Takes a single tile from the bag and adds it to the rack.
    def add_tile_to_rack(self):
        self.rack.append(self.bag.extract_tile())

    # Refills rack to 7 tiles, unless bag is empty. Called upon creation also.
    def replenish_rack(self):
        while len(self.rack) <= 7 and self.bag.get_remaining_tiles() > 0:
            self.add_tile_to_rack()
    
    # Removes a given tile from the array if it exists.
    def remove_tile(self, tile: Tile):
        self.rack.remove(tile)
        
    # Returns the string representaions of each tile on the rack, separated by a ', '.
    def get_rack_str(self):
        return ", ".join(tile.get_letter() for tile in self.rack)
    
    # Returns the number of tiles on the rack
    def rack_length(self):
        return len(self.rack)

    # Returns the list that stores the rack
    def get_rack_ls(self):
        return self.rack

class Player:
    """Represents a player, created anew with a name, and given a score and rack."""

    # Bag needed only to create the rack
    def __init__(self, name: str, bag: Bag) -> None:
        self.name = name
        self.rack = Rack(bag)
        self.score = 0
    
    def get_name(self):
        return self.name
    
    def get_score(self):
        return self.score

    # Returns string representation of the player's rack.
    def get_rack_str(self):
        return self.rack.get_rack_str()
    
    # Returns the player's rack in list form.
    def get_rack_ls(self):
        return self.rack.get_rack_ls()
    
    # Increases the player's score by a given amount.
    def increase_score(self, amount: int):
        self.score += amount

class Board:
    """Represents a standard 15 x 15 board, with '   ' stored as empty spaces, apart from special spaces."""
    
    def __init__(self) -> None:
        self.board = [["   " for i in range(BOARD_SIZE)] for j in range(BOARD_SIZE)]
        self.add_special_spaces()
        self.board[7][7] = " * "
    
    def get_board(self):
        return self.board

    # Adds in the special spaces
    def add_special_spaces(self):
        for coordinate in TRIPLE_WORD_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "TWS"
        for coordinate in TRIPLE_LETTER_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "TLS"
        for coordinate in DOUBLE_WORD_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "DWS"
        for coordinate in DOUBLE_LETTER_SCORE:
            self.board[coordinate[0]][coordinate[1]] = "DLS"
        
    # Borrowed from SM. Only for debugging.
    def print_board(self):
        board_str = "   |  " + "  |  ".join(str(item) for item in range(10)) + "  | " + "  | ".join(str(item) for item in range(10, 15)) + " |"
        board_str += "\n   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _\n"
        board = list(self.board)
        for i in range(len(board)):
            if i < 10:
                board[i] = str(i) + "  | " + " | ".join(str(item) for item in board[i]) + " |"
            if i >= 10:
                board[i] = str(i) + " | " + " | ".join(str(item) for item in board[i]) + " |"
        board_str += "\n   |_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _|\n".join(board)
        board_str += "\n   _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _"
        return board_str

    # Places a validated word on the board.
    def place_word(self, word: str, location: list, direction: Direction, player: Player):
        global SPECIAL_SPOTS
        SPECIAL_SPOTS = []
        word = word.upper()
        n = len(word)

        if direction == Direction.right:
            for i in range(n):
                if self.board[location[0]][location[1] + i] != "   ":
                    SPECIAL_SPOTS.append((word[i], self.board[location[0]][location[1] + i]))
                self.board[location[0]][location[1] + i] = " " + word[i] + " "
        
        elif direction == Direction.down:
            for i in range(n):
                if self.board[location[0] + i][location[1]] != "   ":
                    SPECIAL_SPOTS.append((word[i], self.board[location[0] + i][location[1]]))
                self.board[location[0] + i][location[1]] = " " + word[i] + " "
        
        for tile in player.get_rack_ls():
            if tile.get_letter() in word:
                player.rack.remove(tile)
        player.rack.replenish_rack()

class Word:
    """Represents a word after being submitted by a player."""

    def __init__(self, word: str, board: Board, location: list, direction: Direction, player: Player) -> None:
        self.word = word.upper()
        self.board = board
        self.location = location
        self.direction = direction
        self.player = player

    # Checks if a submitted word can be played.
    def check_word(self, blank_letter=None):
        global round_number, players
        n = len(self.word)
        existing_tiles = ""
        required_tiles = ""

        # Check word out of bounds.
        if not (0 <= self.location[0] < BOARD_SIZE - 1 and 0 <= self.location[1] < BOARD_SIZE - 1):
            return scrabble_error("Word out of bounds")
        if self.direction == Direction.down and (self.location[0] + n - 1 > BOARD_SIZE - 1):
            return scrabble_error("Word out of bounds")
        elif self.direction == Direction.right and (self.location[1] + n - 1 > BOARD_SIZE - 1):
            return scrabble_error("Word out of bounds")
        
        # Check location if play is first play.
        if round_number == 1 and players[0] == self.player and self.location != [7, 7]:
            return scrabble_error("Play first word at star (*) symbol, location 7, 7.")
        
        # Check for blank tile and constructs the word appropriately.
        if blank_letter is not None:
            self.word = self.word[:self.word.index("#")] + blank_letter.upper() + self.word[(self.word.index("#") + 1):]
        
        # Gets existing tiles in the location and direction.
        availables = [" ", "DLS", "DWS", "TLS", "TWS", " * ", "*"]
        if self.direction == Direction.right:
            for i in range(n):
                if self.board.board[self.location[0]][self.location[1] + i] in availables:
                    existing_tiles += " "
                else:
                    existing_tiles += self.board.board[self.location[0]][self.location[1] + i][1]
        elif self.direction == Direction.down:
            for i in range(n):
                if self.board.board[self.location[0] + i][self.location[1]] in availables:
                    existing_tiles += " "
                else:
                    existing_tiles += self.board[self.location[0] + i][self.location[1]][1]
        
        # Check overlap is correct.
        for i in range(n):
            if existing_tiles[i] == " ":
                required_tiles += self.word[i]
            elif existing_tiles[i] != self.word[i]:
                return scrabble_error("Overlap incorrect.")
        
        # Check word is connected to other tiles.
        if (round_number != 1 or (round_number == 1 and players[0] != self.player)) and existing_tiles == " " * n:
            return scrabble_error("Word must connect to other tiles.")
        
        # Ensure word is in dictionary.
        if self.word not in DICTIONARY:
            return scrabble_error("You must enter a valid word.")
        
        # # Check connecting words.
        # top_start = None
        # while top_start not in availables:
        #     pass

    # Calculates and returns the score attained by playing the word
    def calculate_word_score(self):
        score = 0
        for letter in self.word:
            for spot in SPECIAL_SPOTS:
                if letter == spot[0]:
                    if spot[1] == "DLS":
                        score += LETTER_SCORES[letter]
                    elif spot[1] == "TLS":
                        score += LETTER_SCORES[letter] * 2
            score += LETTER_SCORES[letter]
        
        for spot in SPECIAL_SPOTS:
            if spot[1] == "DWS":
                score *= 2
            elif spot[1] == "TWS":
                score *= 3
        
        return score

    def set_word(self, word: str):
        self.word = word.upper()

    def set_location(self, location: list):
        self.location = location
    
    def set_direction(self, direction: Direction):
        self.direction = direction
    
    def get_word(self):
        return self.word

class Game:
    """Represents a game, creating a bag, board, players and related."""

    def __init__(self) -> None:
        self.board = Board()
        self.bag = Bag()
        self.players = []
    
    def set_players(self, names: list):
        num_players = 0
        for name in names:
            self.players.append(Player(name, self.bag))
            num_players += 1
        self.num_players = num_players

    # Starts the game, keeping track of rounds played and skipped, and whether the game is over.
    def start_game(self):
        global round_number, skipped
        self.round_number = 0
        self.skipped = 0
        self.game_over = False
        self.current_player: Player = self.players[0]
        round_number = self.round_number
        skipped = self.skipped
    
    # Performs a play, checking for game details and valididty of the word.
    def turn(self, word_in: str, location: list, direction: Direction):
        if self.bag.get_remaining_tiles() == 0 and self.current_player.rack.rack_length() == 0:
            return self.end_game()
        
        word = Word(word_in, self.board, location, direction, self.current_player)
        checked = word.check_word()
        if not checked:
            return scrabble_error("Invalid word.")
        
        self.board.place_word(word_in, location, direction, self.current_player)
        self.current_player.increase_score(word.calculate_word_score())
        
        curr_index = self.players.index(self.current_player)
        if curr_index == self.num_players - 1:
            self.current_player = self.players[0]
        else:
            self.current_player = self.players[curr_index + 1]
        
        self.round_number += 1

    def skip_turn(self):
        self.skipped += 1

    # Ends the game.
    def end_game(self):
        self.game_over = True
        win_score = 0
        winner = ""
        for player in self.players:
            if player.get_score() > win_score:
                win_score = player.get_score()
                winner = player.get_name()
        
        return (winner, win_score)

def scrabble_error(msg: str):
    # TODO
    pass