# db/apy.py
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter
from defillama2 import DefiLlama
from database_client import DatabaseClient
import numpy as np

# Set pandas display options
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 50)
pd.options.display.float_format = '{:,.4f}'.format

# Set plot styles
plt.rcParams['figure.figsize'] = (10, 6)
plt.style.use("fivethirtyeight")

# Human-readable number formatter
def human_format_dollar_or_num(dollar=False, decimals=0):
    base_fmt = '%.{}f%s'.format(decimals)
    if dollar:
        base_fmt = '$' + base_fmt

    def human_format(num, pos): 
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return base_fmt % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
    
    return human_format

# Fetch and filter APY yields
def fetch_apy_yield():
    obj = DefiLlama()
    df = obj.get_pools_yields()

    # Filter by specific criteria
    is_true = df.index >= 0  # This will select all rows

    cols = ['chain', 'project', 'symbol', 'tvlUsd', 'apyBase', 'apyReward', 'apy', 'apyPct7D', 
            'mu', 'sigma', 'count', 'predictedClass', 'predictedProbability']

    filtered_data = df.loc[is_true, cols].sort_values('apy', ascending=False)

    return filtered_data

# Function to clean the data and handle NaN values
def clean_data(data):
    """Convert NaN values to None and handle other special cases."""
    cleaned_data = []
    for record in data:
        cleaned_record = {k: (None if pd.isna(v) else v) for k, v in record.items()}
        cleaned_data.append(cleaned_record)
    return cleaned_data

# Plot the TVL and APY relationship
def plot_tvl_apy(pool_id, df):
    ax1 = df['tvlUsd'].plot()
    dollar_formatter = FuncFormatter(human_format_dollar_or_num(dollar=True, decimals=0))
    ax1.yaxis.set_major_formatter(dollar_formatter)
    
    for tl in ax1.get_yticklabels():
        tl.set_color('#008FD5')
    ax1.set_ylabel('TVL ($USD)', color='#008FD5')

    ax2 = ax1.twinx()
    ax2.plot(df.index, df['apy'], color='#77AB43')
    ax2.yaxis.set_major_formatter(PercentFormatter(decimals=2))
    
    for tl in ax2.get_yticklabels():
        tl.set_color('#77AB43')
    ax2.set_ylabel('APY', color='#77AB43')

    plt.title(f"Pool ID: {pool_id}")
    plt.show()
 


# Main execution flow
if __name__ == '__main__':
    apy_data = fetch_apy_yield()

    # Convert numpy types to strings (if necessary for your database)
    apy_data = apy_data.apply(lambda x: x.map(lambda y: str(y) if isinstance(y, (np.integer, np.float64)) else y))  # Using apply on columns

    # Convert DataFrame to a list of dictionaries
    apy_data = apy_data.to_dict(orient='records')

    # Clean data to handle NaN and None values
    apy_data = clean_data(apy_data)

    # Debugging print: Check structure of cleaned apy_data
    print("apy_data after cleaning: ", apy_data[:3])  # Show the first few records for validation

    # Choose to save either to a database or to a CSV file
    save_option = input("Choose output (db/csv): ").strip().lower()

    if save_option == 'db':
        db_client = None  # Initialize db_client
        try:
            db_client = DatabaseClient()
            
            # Ensure db_client is connected
            if not db_client.is_connected():
                raise Exception("Database client is not connected.")
            
            # Insert all records at once
            db_client.insert_data(apy_data)
            
        except Exception as e:
            print(f"Error while inserting data into the database: {e}")
        finally:
            if db_client:  # Check if db_client was successfully created
                db_client.close()  # Close the database connection
    elif save_option == 'csv':
        # Convert the DataFrame directly to CSV
        apy_data_df = pd.DataFrame(apy_data)
        apy_data_df.to_csv('apy_yield.csv', index=False)  # Save to CSV
    else:
        print("Invalid option. Exiting.")
