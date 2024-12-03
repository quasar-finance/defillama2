import pandas as pd
from defillama2 import DefiLlama
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Enable CORS for the app
CORS(app)

def fetch_historical_apy_yield(pool_id):
    """Fetch historical APY yields from DefiLlama."""
    obj = DefiLlama()
    df = obj.get_pool_hist_apy(pool_id)
    return df

@app.route('/historical_apy/<string:pool_id>', methods=['GET'])
def get_historical_apy(pool_id):
    try:
        # Fetch historical APY data
        historical_data = fetch_historical_apy_yield(pool_id)

        # Check if data is empty
        if historical_data.empty:
            return jsonify({"message": "No historical data found for the given pool ID."}), 404
    

        # Convert DataFrame to JSON
        historical_data_json = historical_data.to_dict(orient='records')

        return jsonify(historical_data_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def fetch_pools():
    obj = DefiLlama()
    df = obj.get_pools_yields()
    return df

@app.route('/pools', methods=['GET'])
def get_pool_data():
    try:
        # Fetch historical APY data
        pool_data = fetch_pools()

        # Check if data is empty
        if pool_data.empty:
            return jsonify({"message": "Could not fetch pool data from Defillama."}), 404
        
        # Convert DataFrame to JSON
        pool_data_json = pool_data.to_dict(orient='records')

        return jsonify(pool_data_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Print current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5001)
