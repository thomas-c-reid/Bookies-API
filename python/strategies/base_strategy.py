import pandas as pd
import numpy as np
from abc import abstractmethod

class BaseStrategy():
    def __init__(self, file_path):
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def run_strategy(self):
        pass

    @abstractmethod
    def find_error_bets(self):
        pass

    def calculate_results(self):
        pass