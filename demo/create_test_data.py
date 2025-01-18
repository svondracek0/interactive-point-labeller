import pandas as pd
import numpy as np

# Create a date range
date_range = pd.date_range(start='2023-01-01', periods=100, freq='D')

# Create a dataframe
df = pd.DataFrame({
    'date': date_range,
    'value': np.random.randn(100).cumsum(),  # Cumulative sum to simulate a time series
    'outlier': np.random.choice(['no-outlier', 'point', 'seasonal'], size=100)  # Randomly assign annotation options
})

# Save the dataframe to a CSV file
df.to_csv('demo_data.csv', index=False)

print(df.head())