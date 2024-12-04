import pandas as pd
from defillama2 import DefiLlama
import os

def fetch_historical_apy_yield(pool_id):
    """Fetch historical APY yields from DefiLlama."""
    obj = DefiLlama()
    df = obj.get_pool_hist_apy(pool_id)
    return df

def main():
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")

    # Prompt user for pool ID
    pool_id = input("Enter the pool ID: ").strip()

    try:
        # Fetch historical APY data
        historical_data = fetch_historical_apy_yield(pool_id)

        # Check if data is empty
        if historical_data.empty:
            print("No historical data found for the given pool ID.")
            return
        
        # Convert DataFrame to CSV
        output_file = f'historical_apy_{pool_id}.csv'
        historical_data.to_csv(output_file, index=False)
        print(f"Saved historical APY data to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()