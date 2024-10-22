import psycopg2
import pandas as pd

class DatabaseClient:
    def __init__(self, db_path='dbname=mydatabase user=myuser password=password host=localhost'):
        """Initialize the database client and connect to the PostgreSQL database."""
        self.connection = psycopg2.connect(db_path)  # Connect to the specified PostgreSQL database
        self.cursor = self.connection.cursor()  # Create a cursor object to execute SQL commands
        self.create_table()  # Create the table if it doesn't exist

    def is_connected(self):
        """Logic to check if the database connection is active"""
        return self.connection is not None

    def create_table(self):
        """Create the apy_yield table if it doesn't already exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS apy_yield (
            chain TEXT,
            project TEXT,
            symbol TEXT,
            tvlUsd TEXT,  
            apyBase TEXT,   
            apyReward TEXT,   
            apy TEXT,  
            apyPct7D TEXT,   
            mu TEXT,  
            sigma TEXT,   
            count TEXT,  
            predictedClass TEXT,
            predictedProbability TEXT   
        )
        """
        self.cursor.execute(create_table_sql)  # Execute the SQL command to create the table
        self.connection.commit()  # Commit the table creation

    def insert_data(self, data):
        """Insert the fetched APY yield data into the database."""
        insert_sql = """
        INSERT INTO apy_yield (chain, project, symbol, tvlUsd, apyBase, apyReward, apy, 
                               apyPct7D, mu, sigma, count, predictedClass, predictedProbability)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Ensure data is a list of dictionaries
        if isinstance(data, list) and all(isinstance(row, dict) for row in data):
            records = [
                (
                    row.get('chain'), row.get('project'), row.get('symbol'),
                    row.get('tvlUsd'), row.get('apyBase'), row.get('apyReward'), row.get('apy'),
                    row.get('apyPct7D'), row.get('mu'), row.get('sigma'), row.get('count'),
                    row.get('predictedClass'), row.get('predictedProbability')
                )
                for row in data
            ]
            # Execute the insert command for all records
            self.cursor.executemany(insert_sql, records)
            self.connection.commit()  # Commit the changes to the database
        else:
            raise ValueError("Data should be a list of dictionaries")

    def close(self):
        """Close the database connection."""
        self.connection.close()  # Close the database connection

    def fetch_data(self):
        """Fetch all records from the apy_yield table."""
        fetch_sql = "SELECT * FROM apy_yield"  # SQL command to select all records
        self.cursor.execute(fetch_sql)  # Execute the SQL command
        records = self.cursor.fetchall()  # Fetch all records
        return pd.DataFrame(records, columns=[desc[0] for desc in self.cursor.description])  # Convert to DataFrame
