# db/display_db.py
from database_client import DatabaseClient

# Function to display database content
def display_db_content():
    db_client = DatabaseClient()
    data = db_client.fetch_data()  # Assuming fetch_data() retrieves all records
    print(data)  # Display the data
    db_client.close()  # Close the database connection

# Main execution flow
if __name__ == '__main__':
    display_db_content()
