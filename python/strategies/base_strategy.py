import pandas as pd
import numpy as np
from abc import abstractmethod

class beatTheBookies():
    def __init__(self, file_path):
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def run_strategy(self):
        pass

    def calculate_results(self):
        pass