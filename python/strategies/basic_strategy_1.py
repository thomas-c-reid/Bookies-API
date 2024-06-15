import pandas as pd
import numpy as np

# TODO:
# add inheritance from base_strategy

# WAYS TO IMPROVE THIS STRATEGY
# 
# change bet_amount based on some sort of incremental bankroll strategy (need to use bankroll more)
# Would also need to change bet size based on confidence of bet
# Need to make simulate bet a bit more life realistic

class BasicStrategy1():
    def __init__(self, file_path):
        self.name = 'basic_strategy_1_reproduction_of_of_kaggle_code'
        self.bankroll = 1000
        self.bet_amount = 50
        self.margin = 0.05
        self.data = None
        self.file_path = file_path
        self.n_leagues = 0
        self.n_games = 0
        self.result = 0
        self.n_valid_odds = 3
        self.results = {}
        self.load_data()

    def load_data(self):
        self.data = pd.read_csv(self.file_path, compression='gzip', sep=',', quotechar='"')
        self.n_leagues = pd.unique(self.data['league'])
        self.n_games = self.data.shape[0]
        self.result = 0 * (self.data['home_score'] > self.data['away_score']) +\
                      1 * (self.data['home_score'] == self.data['away_score']) +\
                      2 * (self.data['home_score'] < self.data['away_score'])

    # def preprocess_data_for_model(self):
    #     '''
    #     func to sort out data before passing it to model
    #     '''
    #     pass

    # def build_model(self):
    #     '''
    #     function to build model architecture 
    #     '''
    #     pass

    # def train_model(self):
    #     '''
    #     using data see if it can 
    #     '''
    #     pass

    def run_strategy(self):
        '''
        func to run strategy
        '''

        # Calculate margins for home_win, draw, away_win
        earn_margin_home = ((1/self.data['avg_odds_home_win'] - self.margin) * self.data['max_odds_home_win'] - 1) * \
                            (self.data['n_odds_home_win'] > self.n_valid_odds)
        # This last section could get replaced so that it just give it a boost if there are more bookies instead of 
        # It just being some sort of threshold that should get surpassed
        earn_margin_draw = ((1/self.data['avg_odds_draw'] - self.margin) * self.data['max_odds_draw'] - 1) * \
                            (self.data['n_odds_draw'] > self.n_valid_odds)
        earn_margin_away = ((1/self.data['avg_odds_away_win'] - self.margin) * self.data['max_odds_away_win'] - 1) * \
                            (self.data['n_odds_away_win'] > self.n_valid_odds)
        
        # Calculate max_margins
        max_margin = np.max(
            pd.concat(
                [earn_margin_home, earn_margin_draw, earn_margin_away], axis=1
            ), axis=1
        )

        max_arg = pd.concat(
            [earn_margin_home, earn_margin_draw, earn_margin_away], axis=1
        ).apply(np.argmax, axis=1)

        max_margin_max_odds = (max_arg==0) * self.data['max_odds_home_win'] + \
                              (max_arg==1) * self.data['max_odds_draw'] + \
                              (max_arg==2) * self.data['max_odds_away_win']
        
        max_margin_mean_odds = (max_arg==0) * self.data['avg_odds_home_win'] + \
                               (max_arg==1) * self.data['avg_odds_draw'] + \
                               (max_arg==2) * self.data['avg_odds_away_win']
                               
        # Make decision on bet
        should_bet = max_margin > 0
        # TODO: function should output this and then the calc results function should take in some of the other dataframes
        # needed and output whatever statistics we want to show
        # but the main this about this function is to come to a decision

        # TODO: make work for stupid fucking yank odds (im not sure what way they currently work)


        outcome = self.bet_amount * (max_margin_max_odds - 1) * (max_arg == self.result) - self.bet_amount * (max_arg != self.result)

        accuracy = (max_arg == self.result)[should_bet].apply(int)

        self.results['money'] = np.cumsum(outcome[should_bet])
        self.results['accuracy'] = accuracy
        self.results['max_odds'] = max_margin_max_odds[should_bet]
        self.results['mean_odds'] = max_margin_mean_odds[should_bet]
        self.results['ids'] = max_arg.iloc[np.where(should_bet)]
        self.calculate_results()

    def calculate_results(self):
        '''
        This function will output summary statistics about the strategy 

        Results:
            Total Bets Placed:
            Total Bets Examined:
            Should Bet Percentage:
            Avg Home Win Percentage:

            Return:
            Profit:
            MeanAccuracy:
        '''
        totalBets = self.results['money'].shape[0]
        return_var = np.array(self.results['money'])[-1]/(self.results['money'].shape[0] * self.bet_amount) * 100
        profit = np.array(self.results['money'])[-1]

        print(f'Total Bets Examined: {self.n_games}')
        print(f'Total Bets Placed: {totalBets}')
        print(f'Should bet percentage: {totalBets / self.n_games}')
        print(f'Return: {return_var}')
        print(f'Profit: {profit}')

        # TODO
        print(f'Home Win prediction Accuracy')
        print(f'Away Win prediction Accuracy')
        print(f'Draw prediction Accuracy')
        # print(self.results['money'])
        print('finished calculating results')


    def test_data_on_strategy(self):
        '''
        Func to take live score data and output which bets we should bet on based on strategy
        '''
        pass
