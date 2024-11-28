import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, FuncFormatter
from defillama2 import DefiLlama
from database_client import DatabaseClient
import numpy as np
from tabulate import tabulate

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
            'mu', 'sigma', 'count', 'predictedClass', 'predictedProbability', 'pool']

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

     
    apy_data = apy_data.apply(lambda x: x.map(lambda y: str(y) if isinstance(y, (np.integer, np.float64)) else y))  # Using apply on columns
    
    apy_data = apy_data.to_dict(orient='records')

    apy_data = clean_data(apy_data)

     
    print("apy_data after cleaning: ", apy_data[:3])   
     
    save_option = input("Choose output (db/csv): ").strip().lower()

    if save_option == 'db':
        db_client = None   
        try:
            db_client = DatabaseClient()
            
             
            if not db_client.is_connected():
                raise Exception("Database client is not connected.")
            
             
            db_client.insert_data(apy_data)
            
        except Exception as e:
            print(f"Error while inserting data into the database: {e}")
        finally:
            if db_client:   
                db_client.close()   
    elif save_option == 'csv':         
        apy_data_df = pd.DataFrame(apy_data)
        apy_data_df.to_csv('apy_yield.csv', index=False)  # Save to CSV

        # Change filters here to chnage chain, project and symbol for filtered data
        chain = "Base"
        projects = ['aerodrome-v1', 'uniswap-v3']
        symbol = '^USDZ(-|$)'
        base_filtered = apy_data_df[
            (apy_data_df['chain'] == chain) & 
            (apy_data_df['project'].isin(projects)) &
            (apy_data_df['symbol'].str.contains(symbol, na=False))
        ]

        # Save the filtered data to a new CSV
        base_filtered.to_csv(chain + '_filtered.csv', index=False)
    else:
        print("Invalid option. Exiting.")
