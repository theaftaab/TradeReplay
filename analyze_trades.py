import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_trades(tradebook_path='Data/tradebook.csv'):
    # Read the tradebook
    trades_df = pd.read_csv(tradebook_path, parse_dates=['date'])
    
    # Calculate daily returns
    trades_df = trades_df.sort_values('date')
    
    # Calculate daily portfolio value
    trades_df['portfolio_value'] = trades_df['cash_after'] + trades_df['invested_after']
    
    # Create daily portfolio value series
    daily_values = trades_df.groupby('date')['portfolio_value'].last()
    
    # Calculate daily returns
    daily_returns = daily_values.pct_change().fillna(0)
    
    # Calculate cumulative returns
    cumulative_returns = (1 + daily_returns).cumprod() - 1
    
    # Calculate basic metrics
    total_return = cumulative_returns.iloc[-1] - 1
    annualized_return = (1 + total_return) ** (252/len(daily_returns)) - 1
    volatility = daily_returns.std() * np.sqrt(252)
    sharpe_ratio = annualized_return / volatility
    
    # Create plots
    plt.figure(figsize=(15, 10))
    
    # Plot cumulative returns
    plt.subplot(2, 2, 1)
    cumulative_returns.plot()
    plt.title('Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    
    # Plot daily returns distribution
    plt.subplot(2, 2, 2)
    daily_returns.plot(kind='hist', bins=50)
    plt.title('Daily Returns Distribution')
    plt.xlabel('Return')
    plt.ylabel('Frequency')
    
    # Print metrics
    print("\nStrategy Performance Metrics:")
    print(f"Total Return: {total_return:.2%}")
    print(f"Annualized Return: {annualized_return:.2%}")
    print(f"Annualized Volatility: {volatility:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_trades()
