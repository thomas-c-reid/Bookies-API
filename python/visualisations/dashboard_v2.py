import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import os
import sys
import importlib

st.set_page_config(layout="wide")

# TODO
# 1. add in risk metrics
# 2. add in ability to compare against random strategy
# 3. add better functionality to see what the best bets of the day are
# 3.1 only show 'should_bet' dicts but have toggle to show all (automatically off)
# 3.2 build them out into rows in a database with sort as max margin or some shit (don't like the way the jsons are being displayed)

# Metrics to add
# 1. No profitable days vs No losing days

root_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_path)
beat_the_bookies_url = '../../data/beatTheBookies/closing_odds.csv.gz'

strategy_mapping = {
    'strategy3': ('basic_strategy_3', 'strategy3'),
    'strategy1': ('basic_strategy_1', 'strategy1'),
    'RandomStrategy': ('random_strategy', 'randomStrategy'),
}

def load_data(filename):
    data = pd.read_csv(filename)
    data['date'] = pd.to_datetime(data['date'])
    data['total_cash'] = data['total_cash'].astype(float)
    data.set_index('date', inplace=True)
    beat_the_bookies = pd.read_csv(beat_the_bookies_url, compression='gzip', sep=',', quotechar='"')
    return data, beat_the_bookies

def load_strategy_information(strategy_csv):
    strategy_name = os.path.splitext(os.path.basename(strategy_csv))[0]
    module_name, class_name = strategy_mapping.get(strategy_name, (None, None))
    if module_name and class_name:
        module = importlib.import_module(f'strategies.{module_name}')
        strategy_class = getattr(module, class_name)
        strategy_instance = strategy_class(beat_the_bookies_url, dashboard_mode=True)
        return strategy_instance.description
    return "Description not available."

data_dir = '../../data/dailyResults'
files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
file_options = {f"{os.path.splitext(f)[0]}": os.path.join(data_dir, f) for f in files}

selected_strategy = st.sidebar.selectbox("Select a Strategy", options=list(file_options.keys()))
data_file = file_options[selected_strategy]
data, beat_the_bookies = load_data(data_file)
strategy_name = os.path.splitext(os.path.basename(data_file))[0]

app_mode = st.sidebar.selectbox("Choose the mode:",
                                ["View Results", "Test Strategy"])

if app_mode == "View Results":

    description = load_strategy_information(strategy_name)
    st.write(description)

    # Creating metrics variables
    win_rate = round((data['number_of_wins'].sum() / data['number_of_bets'].sum()) * 100, 2)
    number_of_bets = data['number_of_bets'].sum()
    percentage_bet_on = round((number_of_bets / beat_the_bookies.shape[0]) * 100, 2)
    expected_value = round(((data['daily_profit'].sum() - data['daily_losses'].sum()) / data['number_of_bets'].sum()) / 100, 2)
    avg_win = round(data['daily_profit'].sum() / data['number_of_wins'].sum(), 2)
    avg_loss = round(data['daily_losses'].sum() / data['number_of_losses'].sum(), 2)

    # AI GENERATED - NEEDS TESTING
    avg_profit_per_bet = round(data['total_daily_profit'].sum() / number_of_bets, 2)

    # AI GENERATED - NEEDS TESTING
    median_profit_per_bet = round(data['total_daily_profit'].median() / number_of_bets, 2)

    # AI GENERATED - NEEDS TESTING
    running_max = data['total_cash'].cummax()
    drawdowns = running_max - data['total_cash']
    max_drawdown = drawdowns.max()

    # AI GENERATED - NEEDS TESTING
    win_loss_ratio = data['number_of_wins'].sum() / data['number_of_losses'].sum() if data['number_of_losses'].sum() != 0 else float('inf')

    # AI GENERATED - NEEDS TESTING
    returns = data['total_daily_profit'].diff() / number_of_bets
    sharpe_ratio = (returns.mean() / returns.std()) if returns.std() != 0 else float('inf')

    # AI GENERATED - NEEDS TESTING
    volatility = returns.std()

    # Plotting the line chart
    st.write('Total Cash over time')
    st.line_chart(data['total_cash'])

    # Displaying metrics in a grid layout
    st.write("## Metrics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label='Total Number of Bets', value=number_of_bets)
        st.metric(label='Percentage Bet on', value=f'{percentage_bet_on}%')
        st.metric(label='Avg win rate', value=win_rate)

    with col2:
        st.metric(label='Avg profit per bet', value=avg_profit_per_bet)
        st.metric(label='Avg bet loss', value=avg_loss)

        st.metric(label='Ex value of bet', value=expected_value)

    with col3:
        st.metric(label='Max drawdown', value=max_drawdown)
        # look at how this should get calculated for a time series
        st.metric(label='Sharpe Ratio', value=format(float(sharpe_ratio), 'f'))
        st.metric(label='Volatility', value=format(float(volatility), 'f'))

elif app_mode == "Test Strategy":
    st.header("Test Strategy Bets")
    st.write('This will search the matches today and test them against this strategy deciding if they are worthwhile of a bet')

    strategy_file = file_options[selected_strategy]
    strategy_name = os.path.splitext(os.path.basename(strategy_file))[0]
    module_name, class_name = strategy_mapping.get(strategy_name, (None, None))

    if st.button('Run Strategy Test'):
        if module_name and class_name:
            module = importlib.import_module(f'strategies.{module_name}')
            strategy_class = getattr(module, class_name)
            strategy_instance = strategy_class(beat_the_bookies_url, dashboard_mode=True)
            bets = strategy_instance.test_daily_bet_data()
            if bets:
                st.write("Bets Generated:")
                for bet in bets:
                    st.json(bet)
            else:
                st.write("No bets generated.")
