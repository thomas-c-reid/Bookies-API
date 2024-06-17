import pandas as pd
import numpy as np
from datetime import datetime
from json import loads
import matplotlib.pyplot as plt
from .base_strategy import BaseStrategy

class RandomStrategy(BaseStrategy):
    def __init__(self, file_path, dashboard_mode=False, random_ratio=None):
        self.name = 'random_strategy'
        self.description = '''This betting strategy will output X amounts of bets which it has chosen at random to pick'''
        self.bankroll = 1000
        self.initial_bankroll = 1000
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
        self.selected_sports = ['soccer_uefa_european_championship.csv']
        self.daily_results_columns = [
            'date', 'total_daily_profit', 'number_of_bets', 'number_of_wins',
            'number_of_losses', 'daily_profit', 'daily_losses', 'total_cash'
        ]
        if dashboard_mode:
            self.daily_results_csv_url = '../../data/dailyResults/strategy1.csv'
            self.oddsForEventBaseURL = '../../data/oddsForEvent/'
        else:
            self.oddsForEventBaseURL = '../data/oddsForEvent/'
            self.daily_results_csv_url = '../data/dailyResults/randomStrategy.csv'

        if random_ratio is not None:
            self.random_ratio = random_ratio
        else:
            self.random_ratio = 0.11

    def load_data(self):
        self.data = pd.read_csv(self.file_path, compression='gzip', sep=',', quotechar='"')
        self.n_leagues = pd.unique(self.data['league'])
        self.n_games = self.data.shape[0]
        self.result = 0 * (self.data['home_score'] > self.data['away_score']) +\
                      1 * (self.data['home_score'] == self.data['away_score']) +\
                      2 * (self.data['home_score'] < self.data['away_score'])

    def run_strategy(self, verbose=False, save_data=True):
        self.data['match_date'] = pd.to_datetime(self.data['match_date'])

        # TODO: Check that this does it on a day to day basis as I am worried different kick off times will result in a different itteration
        grouped_data = self.data.groupby('match_date')

        money_total = []
        accuracy_total = []
        max_odds_total = []
        mean_odds_total = []
        ids_total = []
        wins = []
        loss = []
        total_won = []
        total_lost = []

        daily_results = pd.DataFrame(columns=self.daily_results_columns)

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

            max_arg_daily = pd.concat(
                [earn_margin_home_daily, earn_margin_draw_daily, earn_margin_away_daily], axis=1
            ).apply(np.argmax, axis=1)

            max_margin_max_odds_daily = (max_arg_daily==0) * group['max_odds_home_win'] + \
                                (max_arg_daily==1) * group['max_odds_draw'] + \
                                (max_arg_daily==2) * group['max_odds_away_win']
            
            max_margin_mean_odds_daily = (max_arg_daily==0) * group['avg_odds_home_win'] + \
                                (max_arg_daily==1) * group['avg_odds_draw'] + \
                                (max_arg_daily==2) * group['avg_odds_away_win']
            

            
            should_bet = self.pick_random_bets(group)

            # outcome = self.bet_amount * (max_margin_max_odds_daily - 1) * (max_arg_daily == result) - self.bet_amount * (max_arg_daily != result)
            outcome = self.bet_amount * (max_margin_max_odds_daily - 1) * (max_arg_daily == result) - self.bet_amount * (max_arg_daily != result)
            outcome = outcome[should_bet]

            num_bets_placed = should_bet.sum()
            num_wins = (max_arg_daily == result)[should_bet].sum()
            num_losses = num_bets_placed - num_wins

            # accuracy = ((max_arg_daily == result) & should_bet).astype(int)
            accuracy = num_wins / (num_wins + num_losses) if (num_wins + num_losses) > 0 else 0
            
            
            money_total.append((outcome[should_bet]))
            accuracy_total.append(accuracy)
            max_odds_total.append(max_margin_max_odds_daily[should_bet])
            mean_odds_total.append(max_margin_mean_odds_daily[should_bet])
            ids_total.append(max_arg_daily.iloc[np.where(should_bet)])
            wins.append(num_wins)
            loss.append(num_losses)

            total_won.append(outcome[outcome > 0].sum())
            total_lost.append(outcome[outcome < 0].sum())

            self.bankroll += sum(outcome[should_bet])

            if verbose:
                print('*'*50)
                print(f'Days profit: {sum(outcome[should_bet])}')
                print(f'number of bets placed: {len(outcome[should_bet])}')
                if len(outcome[should_bet]) > 0:
                    best_bet_today = outcome[should_bet].max()
                    worst_bet_today = outcome[should_bet].min()
                    print(f'Bets Won: {num_wins} , Bets lost: {num_losses}, accuracy: {accuracy}')
                    print(f"Day: {name.date()} - Best Bet: {best_bet_today}, Worst Bet: {worst_bet_today}")
                else:
                    print(f"Day: {name.date()} - No bets placed.")
                print(f'Current Bankroll: {self.bankroll}')
                print('*'*50)

            daily_profit = outcome[outcome > 0].sum()
            daily_loss = outcome[outcome < 0].sum()
            net_daily_profit = outcome.sum()

            if save_data:
                current_day_results = pd.DataFrame({
                'date': [name.date()],
                'total_daily_profit': [round(net_daily_profit, 2)],
                'number_of_bets': [len(outcome[should_bet])],
                'number_of_wins': [num_wins],
                'number_of_losses': [num_losses],
                'daily_profit': [round(daily_profit, 2)],
                'daily_losses': [round(daily_loss, 2)],
                'total_cash': [round(self.bankroll, 2)]
            })

            # Append day's results to the DataFrame using concat
            daily_results = pd.concat([daily_results, current_day_results], ignore_index=True)

        if save_data:
            daily_results.to_csv(self.daily_results_csv_url, index=False)
            print(f"Results saved to {self.daily_results_csv_url}")


        self.results['money'] = np.cumsum(np.concatenate(money_total))
        self.results['accuracy'] = np.mean(accuracy_total)
        self.results['max_odds'] = np.cumsum(np.concatenate(max_odds_total))
        self.results['mean_odds'] = np.cumsum(np.concatenate(mean_odds_total))
        self.results['ids'] = np.cumsum(np.concatenate(ids_total))
        self.results['wins'] = np.sum(wins)
        self.results['loss'] = np.sum(loss)
        self.results['total_won'] = np.sum(total_won)
        self.results['total_lost'] = np.sum(total_lost)

        self.calculate_results()
        error, info, error_dates = self.find_error_bets()
        if error:
            print(info)
        else:
            print('ALL BETS WERE TRUE')

    def calculate_results(self):
        totalBets = self.results['money'].shape[0]
        return_var = np.array(self.results['money'])[-1]/(self.results['money'].shape[0] * self.bet_amount) * 100
        profit = np.array(self.results['money'])[-1]

        print(f'Total Bets Examined: {self.n_games}')
        print(f'Total Bets Placed: {totalBets}')
        print(f'Bet percentage: {totalBets / self.n_games}')
        print(f"Number of bets won:  {self.results['wins']}")
        print(f"Number of bets lost: {self.results['loss']}")
        print(f"Total Won:  {self.results['total_won']}") # Out of all bets placed, the ones that won, how much they add up to
        print(f"Total lost:  {self.results['total_lost']}") # Out of all bets placed, the ones that won, how much they add up to
        print(f'Return: {return_var}')
        print(f'Profit: {profit}')
        print(f'Final Bankroll: {self.bankroll}')
        print('finished calculating results')

    def find_error_bets(self):
        '''
        Go through the created csv for running the simulation and find any days where
        This will help you debug any potential differences in your results
        '''
        error = False # If you find an error anywhere you switch this value to False
        data = pd.read_csv(self.daily_results_csv_url)
        info = ''
        error_dates = set()
        previous_cash = self.initial_bankroll
        tolerance = 0.1

        for index, row in data.iterrows():
            date = row['date']
            total_daily_profit = row['total_daily_profit']

            expected_total_cash = previous_cash + total_daily_profit
            cash_difference = row['total_cash'] - expected_total_cash
            if abs(cash_difference) > 0.01:
                error = True
                error_dates.add(date)
                # difference = row['total_cash'] - (previous_cash + total_daily_profit)
                info += f'ERROR on {date} | total_cash != previous_cash + daily_profit (difference of {cash_difference}) \n'
                info += f"ERROR on {date} | {row['total_cash']} != {previous_cash} + {total_daily_profit} (difference of {cash_difference}) \n" 

            expected_daily_profit = row['daily_profit'] + row['daily_losses']
            profit_difference = total_daily_profit - expected_daily_profit
            if abs(profit_difference) > tolerance:
            # if total_daily_profit != (row['daily_profit'] + row['daily_losses']):
                error = True
                error_dates.add(date)
                # difference = total_daily_profit - (row['daily_profit'] + row['daily_losses'])
                info += f'ERROR on {date} | total_daily_profit != daily_profit + daily_losses (difference of {profit_difference}) \n'   
                info += f"ERROR on {date} | {total_daily_profit} != {row['daily_profit']} + {row['daily_losses']} (difference of {profit_difference}) \n"   
            previous_cash = row['total_cash']

        if error_dates:
                percentage_of_error_days = len(error_dates) / len(data) * 100
                info += f'Total percentage of error dates: {percentage_of_error_days:.2f}% ({len(error_dates)}/{len(data)})'

        return error, info, pd.Series(list(error_dates))

    def pick_random_bets(self, group):
        '''
        This will output a series where the odds of picking a bet are able to be changed
        and returns a boolean Series where True indicates a bet should be placed.
        '''
        should_bet = pd.Series(np.random.rand(group.shape[0]) < self.random_ratio, index=group.index)
        return should_bet