from Values import *
from random import shuffle

class Tile:

    def __init__(self, letter) -> None:
        self.letter = letter.upper()
        if self.letter in SCORES:
            self.score = SCORES[self.letter]
        else:
            self.score = 0
    
    def __eq__(self, other) -> bool:
        if self == other:
            return True
        if isinstance(other, Tile):
            return self.get_letter() == other.get_letter() and self.get_score() == other.get_score()
        return False
    
    def get_letter(self):
        return self.letter

    def get_score(self):
        return self.score

class Bag:

    def __init__(self) -> None:
        self.bag = []
        for letter in LETTER_COUNTS.keys():
            self.add_tile(Tile(letter), LETTER_COUNTS.get(letter))
        shuffle(self.bag)
        
    
    def add_tile(self, tile, count):
        for i in range(count):
            self.bag.append(tile)

    def draw_tile(self):
        return self.bag.pop()
    
    def count_remaining(self):
        return len(self.bag)


class Rack:
    
    def __init__(self, bag) -> None:
        self.rack = []
        self.bag = bag
        for i in range(7):
            self.add_tile()
    
    def add_tile(self):
        self.rack.append(self.bag.draw_tile())
    
    def to_str(self):
        return "[" + ", ".join(letter.get_letter() for letter in self.rack) + "]"
    
    def get_rack(self):
        return self.rack
    
    def remove_tile(self, tile):
        self.rack.remove(tile)
    
    def rack_length(self):
        return len(self.rack)
    
    def refill(self):
        while self.rack_length() < 7 and self.bag.count_remaining() > 0:
            self.add_tile()


class Word:

    def __init__(self, word, location, orientation) -> None:
        self.word = word
        self.location = location
        self.orientation = orientation
    
    def validate_word(self):
        pass

# class Board:

#     def __init__(self) -> None:
#         self.board = [[" " for j in range(15)] for i in range(15)]
