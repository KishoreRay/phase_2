import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm

# Load the CSV file
csv_file = "temp_file_tags.csv"  # Update with actual CSV file path
df = pd.read_csv(csv_file)

# Convert tags column to JSONB format
df["tags"] = df["tags"].apply(lambda x: json.dumps(x.split(", ")) if pd.notna(x) else "[]")

# Database connection parameters
db_params = {
    "dbname": "demo",
    "user": "postgres",
    "password": "pass123#$",
    "host": "localhost",
    "port": "5432"
}

# SQL query for updating data
update_query = """
UPDATE file_metadata
SET tags = %s
WHERE file_path = %s;
"""

# Connect to PostgreSQL and update data
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Convert DataFrame to list of tuples
    data = df[["tags", "file_path"]].where(pd.notna(df), None).to_records(index=False).tolist()

    # Execute batch update with progress bar
    for record in tqdm(data, desc="Updating tags", unit="record"):
        cursor.execute(update_query, record)
    conn.commit()

    print("Tags updated successfully!")

except Exception as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()