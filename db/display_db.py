from database_client import DatabaseClient

 
def display_db_content():
    db_client = DatabaseClient()
    data = db_client.fetch_data()   
    print(data)   
    db_client.close()   

 
if __name__ == '__main__':
    display_db_content()
