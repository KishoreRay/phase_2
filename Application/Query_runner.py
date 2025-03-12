import psycopg2
from psycopg2.extras import RealDictCursor
from Query_generator import get_query

# Database connection parameters
db_params = {
    "dbname": "demo",
    "user": "postgres",
    "password": "pass123#$",
    "host": "localhost",
    "port": "5432"
}

def query_database(query):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        
        # Create a cursor that returns results as dictionaries
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Print results
        for row in results:
            print(dict(row))
            
        return results
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        cursor.close()
        conn.close()

# Example custom query
def get_result(user_query):
    custom_query = get_query(user_query)
    return query_database(custom_query)