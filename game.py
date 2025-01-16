import random
from typing import Optional
import env, lib
class Card:
    def __init__(self, suit, val):
        self.suit = suit
        self.value = val

    def __str__(self):
        value = self.value
        if value == 1: value = 'A'
        elif value == 11: value = 'J'
        elif value == 12: value = 'Q'
        elif value == 13: value = 'K'
        return f"{value} of {self.suit}"

    def __eq__(self, other):
        if isinstance(other, Card):
            value = other.value
        else:
            value = other
        return self.value == value 

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for s in ["♠️", "♥️", "♦️", "♣️"]:
            for v in range(1, 14):
                self.cards.append(Card(s, v))
        # input jokers
        for i in range(2):
            self.cards.append(Card('🤡', 0))

    def show(self):
        for c in self.cards:
            c.show()

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawCard(self):
        return self.cards.pop()


class Player:
    drew = False
    def __init__(self, name):
        self.name = name
        self.hand = []


    def draw(self, deck):
        ans = deck.drawCard()
        if not ans: return
        self.hand.append(ans)
        return ans

    def show_hand(self):
        return [str(card) for card in self.hand]
    
    def __str__(self):
        return self.name

class Game:
    length = 0
    reversed = False 
    highest = None

    def __str__(self):
        return f'''\n player: {self.current_player} \n
            player_list: {[str(player) for player in self.players]} \n
            cards: {[len(player.hand) for player in self.players]} \n
            highest: {self.highest} \n
            current_player: {self.current_player} \n
            starter: {self.starter} \n
            reversed: {self.reversed}\n'''

    def find_player(self, name) -> Optional[Player]:
        for player in self.players:
            if player.name == name:
                return player
        return

    def __init__(self, players):
        self.deck = Deck()
        self.deck.shuffle()
        self.players = []
        for player in players:
            self.players.append(Player(player))

    def start(self):
        'Start the game'
        for player in self.players:
            for i in range(env.init_card_per_player):
                player.draw(self.deck)
        'Decide the player who starts the game'
        self.current_id = random.randint(0, len(self.players) - 1)
        self.current_player = self.players[self.current_id]
        self.starter = self.current_player


    def clear_round(self):
        'Clear the round'
        self.highest = None
        self.starter = self.current_player

    def compare(self, comb, highest):
        'return True if power1 > power2 in current sense'
        if not highest: return True, ''
        message = ''
        power1 = comb.power
        power2 = highest.power
        if power1 == 57: return True, 'Grothendieck Prime'
        if power1 == 1729:
            self.reversed = not self.reversed
            return True, 'Ramanujan Number'
        if comb.length != highest.length:
            res = False
            message = 'Cards length not equal'
        elif self.reversed:
            res =  power1 < power2
        else:
            res =  power1 > power2
        if not res:
            message = 'greater' if self.reversed else 'smaller'
            message = f'Card power should be {message} than the previous one, which is {power2}'
        return res, message

    def empty(self):
        for player in self.players:
            if len(player.hand) != 0:
                return False
        return True

    def play(self, statement):
        'Let current player play'
        comb = lib.get_cards(statement)
        if not comb: return None, 'Expression illegal'
        numbers= comb.numbers
        cards = [Card('Spades', int(number)) for number in numbers]
        if not cards: return None, 'Cards illegal'
        if self.current_player == self.starter:
            self.clear_round()
        ok, message = self.compare(comb, self.highest)
        if not ok:
            return False, message 
        hand_copy = self.current_player.hand.copy()
        for card in cards:
            if card not in hand_copy:
                # for i in range(len(cards)):
                    # self.current_player.draw(self.deck)
                return False, f'Card {card} not in hand, punish {len(cards)}'
            hand_copy.remove(card)
        for card in cards:
            self.current_player.hand.remove(card) 
        if not self.empty(): self.skip()
        self.highest = comb
        self.starter = self.current_player
        return True, f'Cards played by {self.current_player} successfully'
            
    def draw(self):
        'Draw a card for the current player'
        if not self.current_player.drew:
            ans = self.current_player.draw(self.deck)
            if not ans: return False, 'No card left'
            self.current_player.drew = True
            return True, f'{self.current_player} drew a card'
        return False, f'{self.current_player} already drew a card'

    def skip(self):
        'Skip the current player'
        self.current_id = (self.current_id + 1) % len(self.players)
        self.current_player.drew = False
        self.current_player = self.players[self.current_id]
        if len(self.current_player.hand) == 0:
            self.skip()

        
if __name__ == '__main__':
    pass

    
