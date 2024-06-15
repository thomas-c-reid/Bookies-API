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

    def run_strategy(self):
        '''
        func to run strategy
        '''
        self.data['match_date'] = pd.to_datetime(self.data['match_date'])

        # TODO: Check that this does it on a day to day basis as I am worried different kick off times will result in a different itteration
        grouped_data = self.data.groupby('match_date')

        money_total = []
        accuracy_total = []
        max_odds_total = []
        mean_odds_total = []
        ids_total = []
        for name, group in grouped_data:
            result = 0 * (group['home_score'] > group['away_score']) +\
                      1 * (group['home_score'] == group['away_score']) +\
                      2 * (group['home_score'] < group['away_score'])

            earn_margin_home_daily = ((1/group['avg_odds_home_win'] - self.margin) * group['max_odds_home_win'] - 1) * \
                                     (group['n_odds_home_win'] > self.n_valid_odds)  
            earn_margin_draw_daily = ((1/group['avg_odds_draw'] - self.margin) * group['max_odds_draw'] - 1) * \
                                     (group['n_odds_draw'] > self.n_valid_odds)  
            earn_margin_away_daily = ((1/group['avg_odds_away_win'] - self.margin) * group['max_odds_away_win'] - 1) * \
                                     (group['n_odds_away_win'] > self.n_valid_odds)  
            
            max_margin_daily = np.max(
                pd.concat(
                    [earn_margin_home_daily, earn_margin_draw_daily, earn_margin_away_daily], axis=1
                ), axis=1
            )

            max_arg_daily = pd.concat(
                [earn_margin_home_daily, earn_margin_draw_daily, earn_margin_away_daily], axis=1
            ).apply(np.argmax, axis=1)

            max_margin_max_odds_daily = (max_arg_daily==0) * group['max_odds_home_win'] + \
                                (max_arg_daily==1) * group['max_odds_draw'] + \
                                (max_arg_daily==2) * group['max_odds_away_win']
            
            max_margin_mean_odds_daily = (max_arg_daily==0) * group['avg_odds_home_win'] + \
                                (max_arg_daily==1) * group['avg_odds_draw'] + \
                                (max_arg_daily==2) * group['avg_odds_away_win']
            
            # should_bet_daily = max_margin_daily > 0

            bet_size, should_bet_daily = self.calculate_bet_size(max_margin_daily, self.bet_amount, self.bankroll)

            outcome = bet_size * (max_margin_max_odds_daily - 1) * (max_arg_daily == result) - bet_size * (max_arg_daily != result)
            accuracy = (max_arg_daily == result)[should_bet_daily].apply(int)

            money_total.append((outcome[should_bet_daily]))
            accuracy_total.append(accuracy)
            max_odds_total.append(max_margin_max_odds_daily[should_bet_daily])
            mean_odds_total.append(max_margin_mean_odds_daily[should_bet_daily])
            ids_total.append(max_arg_daily.iloc[np.where(should_bet_daily)])

            self.bankroll += sum(outcome[should_bet_daily])

            print('*'*50)
            print(f'Days profit: {sum(outcome[should_bet_daily])}')
            print(f'number of bets placed: {len(outcome[should_bet_daily])}')
            if len(outcome[should_bet_daily]) > 0:  # Ensure there are bets today to avoid errors
                best_bet_today = outcome[should_bet_daily].max()
                worst_bet_today = outcome[should_bet_daily].min()
                print(f"Day: {name.date()} - Best Bet: {best_bet_today}, Worst Bet: {worst_bet_today}")
            else:
                print(f"Day: {name.date()} - No bets placed.")
            print(f'Current Bankroll: {self.bankroll}')
            print('*'*50)

        self.results['money'] = np.cumsum(np.concatenate(money_total))
        self.results['accuracy'] = np.cumsum(np.concatenate(accuracy_total))
        self.results['max_odds'] = np.cumsum(np.concatenate(max_odds_total))
        self.results['mean_odds'] = np.cumsum(np.concatenate(mean_odds_total))
        self.results['ids'] = np.cumsum(np.concatenate(ids_total))

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
        print(f'Final Bankroll: {self.bankroll}')

        # TODO
        # print(f'Home Win prediction Accuracy')
        # print(f'Away Win prediction Accuracy')
        # print(f'Draw prediction Accuracy')
        print('finished calculating results')

    def calculate_bet_size(self, max_margin_daily, bet_amount, bankroll):
        staked_money = bankroll/10


        # The initial bet size is zero
        bet_size = pd.Series(0, index=max_margin_daily.index)

        # Places where you should place a bet
        should_bet_daily = max_margin_daily > 0

        # Set initial bet amounts where it's valid to bet
        bet_size[should_bet_daily] = bet_amount

        # Calculate additional amounts to bet based on how much the margin exceeds 0.1
        additional_amounts = 10 * np.floor((max_margin_daily - 0.1) / 0.1)

        # Add these additional amounts to the bet size where the margin is above 0.1
        bet_size[max_margin_daily > 0.1] += additional_amounts[max_margin_daily > 0.1]

        return bet_size, should_bet_daily


    def test_data_on_strategy(self):
        '''
        Func to take live score data and output which bets we should bet on based on strategy
        '''
        pass
