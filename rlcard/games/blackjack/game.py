import random
from os import path
import sys
from copy import deepcopy
FILE = path.abspath(__file__)
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(FILE)))))
from rlcard.core import Game
from rlcard.games.blackjack.dealer import BlackjackDealer as Dealer
from rlcard.games.blackjack.player import BlackjackPlayer as Player
from rlcard.games.blackjack.round import BlackjackRound as Round
from rlcard.games.blackjack.judger import BlackjackJudger as Judger

class BlackjackGame(Game):
    def __init__(self, seed=None):
        super().__init__()
        self.set_seed(seed)
        self.dealer = Dealer()
        self.player = Player(0)
        self.judger = Judger()
        self.winner = {'dealer':0, 'player':0}
        #self.winner = {self.player.get_player_id()+1:0, self.player.get_player_id():0}
        self.init()
        self.history = []

    def get_player_num(self):
        return 1

    def set_seed(self, seed):
        random.seed(seed)

    def start_game(self):
        player = self.player.get_player_id()
        #state = self.get_state(player)
        action = ['hit', 'stand']
        self.init()
        while not self.end():
            act = random.choice(action)
            print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
            print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
            print("Player_action:",act)
            next_state, next_player = self.step(act)

        print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
        print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
        print(self.winner)

    def get_player_id(self):
        return self.player.get_player_id()

    def get_state(self, player):
        state = {}
        state['actions'] = ('hit', 'stand')
        hand = [card.get_index() for card in self.player.hand]
        dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]
        state['state'] = (hand, dealer_hand)
        return state

    def init(self):
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.player.status, self.player.score = self.judger.judge_round(self.player)
        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
        #p = deepcopy(self.player)
        #d = deepcopy(self.dealer)
        #self.history = [(d,p)]
            
    def step(self, action):
        next_state = {}
        p = deepcopy(self.player)
        d = deepcopy(self.dealer)
        self.history.append((d,p))
        if action != "stand":
            self.dealer.deal_card(self.player)
            self.player.status, self.player.score = self.judger.judge_round(self.player)
            if self.player.status == 'bust':
                self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player.hand]
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]
            next_state['state'] = (hand, dealer_hand)
            next_state['actions'] = ('hit', 'stand')

        elif action == "stand":
            while self.judger.judge_score(self.dealer.hand) < 17:
                self.dealer.deal_card(self.dealer)
                self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
            self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player.hand]
            dealer_hand = [c.get_index() for c in self.dealer.hand[1:]]
            next_state['state'] = (hand, dealer_hand) # show all hand of dealer
            next_state['actions'] = ('hit', 'stand')
        return next_state, self.player.get_player_id()

    def step_back(self):
        self.dealer, self.player = self.history.pop()

    def end(self):
        if self.player.status == 'bust'or self.dealer.status == 'bust' or (self.winner['dealer'] != 0 or self.winner['player'] != 0):
            return True
        else:
            return False
        
    def reset(self):
        self.winner = {'dealer':0, 'player':0}
        #self.winner = {self.player.get_player_id()+1:0, self.player.get_player_id():0}
        self.dealer = Dealer()
        self.player = Player(0)
        self.judger = Judger()
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.player.status, self.player.score = self.judger.judge_round(self.player)
        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)

    def get_reward(self):
        pass

if __name__ == "__main__":
    game = BlackjackGame()
    game.start_game()