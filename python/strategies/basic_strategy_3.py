import pandas as pd
import numpy as np
from datetime import datetime
from json import loads
# TODO:
# add inheritance from base_strategy

# WAYS TO IMPROVE THIS STRATEGY
# 
# change bet_amount based on some sort of incremental bankroll strategy (need to use bankroll more)
# Would also need to change bet size based on confidence of bet
# Need to make simulate bet a bit more life realistic

class BasicStrategy3():
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
        self.oddsForEventBaseURL = 'data/oddsForEvent/'
        self.selected_sports = ['soccer_uefa_european_championship.csv']

    # Simulation Functions
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

            bet_size, should_bet_daily = self.calculate_bet_size(max_margin_daily, self.bet_amount, self.bankroll, group['n_odds_away_win'])

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

    def calculate_bet_size(self, max_margin_daily, bet_amount, bankroll, number_of_bookies):

        staked_money = bankroll*0.2
        
        # The initial bet size is zero
        bet_size = pd.Series(0, index=max_margin_daily.index)

        # Places where you should place a bet
        should_bet_daily = max_margin_daily > 0

        # Set initial bet amounts where it's valid to bet
        bet_size[should_bet_daily] = bet_amount

        # Calculate additional amounts to bet based on how much the margin exceeds 0.1
        additional_amounts = 10 * np.floor((max_margin_daily - 0.1) / 0.1)

        # Get the number of valid bookies where betting is valid and calculate extra bet amounts for extra bookies
        valid_bookies = number_of_bookies[should_bet_daily]
        extra_bookie_amounts = 5 * (valid_bookies - 3)
        extra_bookie_amounts[extra_bookie_amounts < 0] = 0  # Ensure that we do not subtract from the bet amount if bookies are <= 3

        # Apply the additional amounts where the margin is above 0.1
        bet_size[max_margin_daily > 0.1] += additional_amounts[max_margin_daily > 0.1]

        # Add extra amounts for additional bookies
        bet_size[should_bet_daily] += extra_bookie_amounts

        return bet_size, should_bet_daily

    # TODO
    def save_simulation_returns(self, data):
        '''
        function to save the simulated data about which bets were made
        save to two CSV's (timeseries-bets.csv, simulation_bets_placed)
        '''
        pass
    
    # TODO
    def create_visualisations(self):
        '''
        Function to use the saved simulated data to output graphs about risk/reward for each strategy
        * Maybe this func should go in test.py
        '''
        pass
    
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
        
        self.place_bets(bets)

        # add in functions to properly visualise this data
        # Also to 
