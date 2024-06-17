import pandas as pd # type: ignore
import numpy as np # type: ignore
from datetime import datetime
from json import loads
import matplotlib.pyplot as plt # type: ignore

# TODO:
# add inheritance from base_strategy

# WAYS TO IMPROVE THIS STRATEGY
# 
# change bet_amount based on some sort of incremental bankroll strategy (need to use bankroll more)
# Would also need to change bet size based on confidence of bet
# Need to make simulate bet a bit more life realistic

class strategy2():
    def __init__(self, file_path, dashboard_mode=False):
        self.name = 'Basic Strategy 2'
        self.description = ''' Very basic trading strategy which identifies value bets with while keeping an eye on bankroll'''
        self.bankroll = 10000
        self.initial_bankroll = 10000
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
            self.daily_results_csv_url = '../../data/dailyResults/strategy2.csv'
            self.oddsForEventBaseURL = '../../data/oddsForEvent/'
        else:
            self.oddsForEventBaseURL = '../data/oddsForEvent/'
            self.daily_results_csv_url = '../data/dailyResults/strategy2.csv'

    # Simulation Functions
    def load_data(self):
        self.data = pd.read_csv(self.file_path, compression='gzip', sep=',', quotechar='"')
        self.n_leagues = pd.unique(self.data['league'])
        self.n_games = self.data.shape[0]
        self.result = 0 * (self.data['home_score'] > self.data['away_score']) +\
                      1 * (self.data['home_score'] == self.data['away_score']) +\
                      2 * (self.data['home_score'] < self.data['away_score'])

    def run_strategy(self, verbose=False, save_data=False):
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
            
            bet_size, should_bet_daily = self.calculate_bet_size(max_margin_daily, self.bet_amount, self.bankroll, group['n_odds_away_win'])
            should_bet_indices = should_bet_daily.index[should_bet_daily == 1]

            outcome = bet_size * (max_margin_max_odds_daily - 1) * (max_arg_daily == result) - bet_size * (max_arg_daily != result)
            accuracy = (max_arg_daily == result)[should_bet_indices].apply(int)

            money_total.append((outcome[should_bet_indices]))
            accuracy_total.append(accuracy)
            max_odds_total.append(max_margin_max_odds_daily[should_bet_indices])
            mean_odds_total.append(max_margin_mean_odds_daily[should_bet_indices])
            ids_total.append(max_arg_daily.iloc[np.where(should_bet_indices)])

            self.bankroll += sum(outcome[should_bet_indices])

            if verbose:
                print('*'*50)
                print(f'Days profit: {sum(outcome[should_bet_indices])}')
                print(f'number of bets placed: {len(outcome[should_bet_indices])}')
                if len(outcome[should_bet_indices]) > 0:  # Ensure there are bets today to avoid errors
                    best_bet_today = outcome[should_bet_indices].max()
                    worst_bet_today = outcome[should_bet_indices].min()
                    print(f"Day: {name.date()} - Best Bet: {best_bet_today}, Worst Bet: {worst_bet_today}")
                else:
                    print(f"Day: {name.date()} - No bets placed.")
                print(f'Current Bankroll: {self.bankroll}')
                print('*'*50)

            number_of_wins = accuracy.sum()
            number_of_losses = len(accuracy) - number_of_wins

            # daily_profit = outcome[should_bet_indices & (max_arg_daily == result)].sum()
            # daily_loss = outcome[should_bet_indices & (max_arg_daily != result)].sum()

            daily_profit = outcome[outcome.index.intersection(max_arg_daily[max_arg_daily == result].index)].sum()
            daily_loss = outcome[outcome.index.intersection(max_arg_daily[max_arg_daily != result].index)].sum()

            if save_data:
                current_day_results = pd.DataFrame({
                'date': [name.date()],
                'total_daily_profit': [round(sum(outcome[should_bet_indices]), 2)],
                'number_of_bets': [len(outcome[should_bet_indices])],
                'number_of_wins': [number_of_wins],
                'number_of_losses': [number_of_losses],
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
        self.results['accuracy'] = np.cumsum(np.concatenate(accuracy_total))
        self.results['max_odds'] = np.cumsum(np.concatenate(max_odds_total))
        self.results['mean_odds'] = np.cumsum(np.concatenate(mean_odds_total))
        self.results['ids'] = np.cumsum(np.concatenate(ids_total))

        self.calculate_results()
        error, info, error_dates = self.find_error_bets()
        if error:
            print(info)
        else:
            print('ALL BETS WERE TRUE')

        self.create_visualisations(error_dates)
        

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

        # print(f'Home Win prediction Accuracy')
        # print(f'Away Win prediction Accuracy')
        # print(f'Draw prediction Accuracy')
        print('finished calculating results')

    def calculate_bet_size(self, max_margin_daily, bet_amount, bankroll, number_of_bookies):

        # get top n_bets_to_make index wihin max_margin dail
        # change should_bet_daily to make to values at those indexes turn to one
        # same with bet_size array and the value 50
        # TODO add in number of bookies check

        staked_money = bankroll*0.2
        n_bets_to_make = int(staked_money / 50)

        if n_bets_to_make < 3:
            n_bets_to_make = 3
        
        bet_size = pd.Series(0, index=max_margin_daily.index)
        should_bet_daily = pd.Series(0, index=max_margin_daily.index)

        bet_indicies = max_margin_daily[max_margin_daily > 0].nlargest(n_bets_to_make).index

        should_bet_daily.loc[bet_indicies] = 1
        bet_size.loc[bet_indicies] = 50

        return bet_size, should_bet_daily

    # Visulisations
    def create_visualisations(self, error_dates=None):
        '''
        Function to use the saved simulated data to output graphs about risk/reward for each strategy
        *Graph 1 - total_cash over time
        '''
        data = pd.read_csv(self.daily_results_csv_url)
        data['date'] = pd.to_datetime(data['date'])
        data['total_cash'] = data['total_cash'].astype(float)

        plt.figure(figsize=(10,5))
        plt.plot(data['date'], data['total_cash'], marker='o', linestyle='-', label='Total Cash')
        
        # Adding in dates with errors
        if len(error_dates) > 0:
            error_dates = pd.to_datetime(error_dates)
            error_cash = data[data['date'].isin(error_dates)]['total_cash']

        # # total cash over time
        plt.title(f'Total cash over time for {self.name}')
        plt.xlabel('Date')
        plt.ylabel('Total Cash')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


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

    # Using Live Data Functions
    def process_data_to_test_strategy(self, seleected_date=None):
        # Get todays date
        if seleected_date is None:
            date = str(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))[0:10]
        else:
            # TODO: have it formatted the correct way
            pass

        # For each sport we want to investigate
        for selected_sport in self.selected_sports:
            url = self.oddsForEventBaseURL + selected_sport
            sports_odds = pd.read_csv(url)
            
            # Filter for todays events
            sports_odds['commence_date'] = sports_odds['commence_time'].str[0:10]
            todays_sport_odds = sports_odds[sports_odds['commence_date'] == date]
            todays_sport_odds['bookmakers'] = todays_sport_odds['bookmakers'].apply(loads)
        
            prediction_dicts = []

            # For each event in the sport
            for index, row in todays_sport_odds.iterrows():
                prediction_dict = {}
                home_team = row['home_team']
                away_team = row['away_team']
                sport_title = row['sport_title']

                n_of_bookies = len(row['bookmakers'])

                max_odds_home_win = 0
                max_odds_draw = 0
                max_odds_away_win = 0

                avg_odds_home_win_array = []
                avg_odds_draw_array = []
                avg_odds_away_win_array = []

                best_bookmaker_home_win = None
                best_bookmaker_draw = None
                best_bookmaker_away_win = None
                for bookmaker in row['bookmakers']:
                    bookie = bookmaker.get('key')
                    markets = bookmaker.get('markets')[0]
                    for outcome in markets.get('outcomes'):
                        if outcome.get('name') == home_team:
                            home_team_price = outcome.get('price')
                            if home_team_price > max_odds_home_win:
                                max_odds_home_win = home_team_price
                                best_bookmaker_home_win = bookie
                            avg_odds_home_win_array.append(home_team_price)

                        if outcome.get('name') == away_team:
                            away_team_price = outcome.get('price')
                            if away_team_price > max_odds_away_win:
                                max_odds_away_win = away_team_price
                                best_bookmaker_away_win = bookie
                            avg_odds_away_win_array.append(away_team_price)

                        if outcome.get('name') == 'Draw':
                            draw_price = outcome.get('price')
                            if draw_price > max_odds_draw:
                                max_odds_draw = draw_price
                                best_bookmaker_draw = bookie
                            avg_odds_draw_array.append(draw_price)
                prediction_dict['id'] = row['id']
                prediction_dict['title'] = f'{home_team} V {away_team} - {sport_title}'
                prediction_dict['avg_odds_home_win'] = np.mean(avg_odds_home_win_array)
                prediction_dict['max_odds_home_win'] = max_odds_home_win
                prediction_dict['max_odds_home_win_bookie'] = best_bookmaker_home_win
                prediction_dict['avg_odds_away_win'] = np.mean(avg_odds_away_win_array)
                prediction_dict['max_odds_away_win'] = max_odds_away_win
                prediction_dict['max_odds_away_win_bookie'] = best_bookmaker_away_win
                prediction_dict['avg_odds_draw'] = np.mean(avg_odds_draw_array)
                prediction_dict['max_odds_draw'] = max_odds_draw
                prediction_dict['max_odds_draw_bookie'] = best_bookmaker_draw
                prediction_dict['n_of_bookies'] = n_of_bookies
                prediction_dicts.append(prediction_dict)
        return prediction_dicts
            


            # for bookmaker in todays_sport_odds['bookmakers'].iloc[0]:
            #     print(bookmaker)
            # print(todays_sport_odds.shape)


        pass

    def test_data_on_strategy(self, bets):
        '''
        Func to take live score data and output which bets we should bet on based on strategy

        :avg_odds_home_win - value describing the avg off of a home win (group['avg_home_win'])
        :max_odds_home_win - 
        :avg_odds_away_win - value describing the avg off of a home win (group['avg_home_win'])
        :max_odds_away_win - 
        :avg_odds_draw - value describing the avg off of a home win (group['avg_home_win'])
        :max_odds_draw - 
        :n_of_bookies - 
        '''
        # Clean this function up tmr after you get the data saved the correct way
        # TBF i think you have enough data, you now just need to go and have it formatted the right way to be tested
        for bet_json in bets:
            avg_odds_home_win = bet_json.get('avg_odds_home_win')
            max_odds_home_win = bet_json.get('max_odds_home_win')
            avg_odds_away_win = bet_json.get('avg_odds_away_win')
            max_odds_away_win = bet_json.get('max_odds_away_win')
            avg_odds_draw = bet_json.get('avg_odds_draw')
            max_odds_draw = bet_json.get('max_odds_draw')
            n_bookies = bet_json.get('n_of_bookies')

            earn_margin_home_daily = ((1/avg_odds_home_win - self.margin) * max_odds_home_win - 1) * \
                                        (n_bookies > self.n_valid_odds)  
            earn_margin_draw_daily = ((1/avg_odds_draw - self.margin) * max_odds_draw - 1) * \
                                        (n_bookies > self.n_valid_odds)  
            earn_margin_away_daily = ((1/avg_odds_away_win - self.margin) * max_odds_away_win - 1) * \
                                        (n_bookies > self.n_valid_odds)  
            
            max_margin_daily = np.max([earn_margin_home_daily, earn_margin_draw_daily, earn_margin_away_daily])

            max_arg_daily = pd.DataFrame({
                'home': [earn_margin_home_daily],
                'draw': [earn_margin_draw_daily],
                'away': [earn_margin_away_daily]
            }).apply(np.argmax, axis=1)

            max_margin_max_odds_daily = (max_arg_daily==0) * max_odds_home_win + \
                                (max_arg_daily==1) * max_odds_draw + \
                                (max_arg_daily==2) * max_odds_away_win
            
            max_margin_mean_odds_daily = (max_arg_daily==0) * avg_odds_home_win + \
                                (max_arg_daily==1) * avg_odds_draw + \
                                (max_arg_daily==2) * avg_odds_away_win
            
            # should_bet_daily = max_margin_daily > 0
            bet_json['max_margin'] = max_margin_daily
            bet_json['max_arg'] = max_arg_daily
            bet_json['should_bet'] = max_margin_daily > 0
        return bets

    # TODO
    def place_bets(self, bets):
        '''
        Function for running a simulation of this on live incoming 
        Save each bet that we believe to be worth to a CSV with information about the bet
        '''
        # TODO 
        pass

    # TODO
    def update_placed_bets(self):
        '''
        function to reach out to the scores API and based on each placed bets ID, figure out if it won or lost
        Then save to a new CSV called 'finished_bets' - still need to think about structure
        *You would also have to calculate how much profit you get if you won the bet within this function 
        '''
        pass

    def test_daily_bet_data(self):

        
        bets = self.process_data_to_test_strategy()
        print(f'Created Bets: number of bets({len(bets)})')
        bets = self.test_data_on_strategy(bets)
        for bet in bets:
            print('*'*50)
            print(bet)
            print('*'*50)
        return bets

        # add in functions to properly visualise this data
        # Also to 
