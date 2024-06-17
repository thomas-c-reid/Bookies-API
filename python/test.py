import numpy as np # type: ignore
import pandas as pd # type: ignore
import strategies
import strategies.basic_strategy_3
import strategies.basic_strategy_1
import strategies.basic_strategy_2
import strategies.random_strategy

file_path = '../data/beatTheBookies/closing_odds.csv.gz'
closing_odds = pd.read_csv(file_path, compression='gzip', sep=',', quotechar='"')

class testStrategies():
    def __init__(self):
        self.strategies = []
        self.load_strategies()

    def load_strategies(self):
        # self.strategies.append(strategies.basic_strategy_3.strategy3(file_path))
        self.strategies.append(strategies.basic_strategy_2.strategy2(file_path))
        # self.strategies.append(strategies.basic_strategy_1.strategy1(file_path))
        # self.strategies.append(strategies.random_strategy.RandomStrategy(file_path))

    def run_strategies(self, verbose=False, save_data=False):
        for strat in self.strategies:
            print(f'Beginning to run strategy: {strat.name}')
            strat.run_strategy(verbose=verbose, save_data=save_data)

    def visualise_strategy_results(self):
        for strat in self.strategies:
            print(f'Creating visuasations for {strat.name}')
            strat.create_visualisations()
    
    def test_data_on_strategy(self):
        for strat in self.strategies:
            print(f'Testing live data to run strategy: {strat.name}')
            strat.test_daily_bet_data()

    def update_histories():
        # with any data in the scores file have it update the status of 
        # Do this manually at first, still lots more stuff that would be priority
        pass


main = testStrategies()
main.run_strategies(verbose=True, save_data=True)
# main.visualise_strategy_results()
# main.test_data_on_strategy()



