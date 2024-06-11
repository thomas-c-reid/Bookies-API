import numpy as np
import pandas as pd
import strategies
import strategies.basic_strategy_1

# Initially build out this file to test the random strategy
file_path = 'data/beatTheBookies/closing_odds.csv.gz'
closing_odds = pd.read_csv(file_path, compression='gzip', sep=',', quotechar='"')

class testStrategies():
    def __init__(self):
        self.strategies = []
        self.load_strategies()

    def load_strategies(self):
        self.strategies.append(strategies.basic_strategy_1.BasicStrategy1(file_path))

    def run_strategies(self):
        for strat in self.strategies:
            print(f'Beginning to run strategy: {strat.name}')
            strat.run_strategy()
            strat.calculate_results()


main = testStrategies()
main.run_strategies()



