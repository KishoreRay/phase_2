import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values

# Load the CSV file
csv_file = "New_file_tags copy.csv"  # Update with actual CSV file path
df = pd.read_csv(csv_file)

# Convert tags column to JSONB format
df["tags"] = df["tags"].apply(lambda x: json.dumps(x.split(", ")) if pd.notna(x) else "[]")

# Convert file size from bytes to KB, handling NaN values
df["File_Size"] = df["File_Size"].fillna(0).astype(float) / 1024  # Convert bytes to KB
df["File_Size"] = df["File_Size"].astype(int)  # Ensure integer values

# Handle empty values for timestamps
df["File_Created"] = df["File_Created"].where(pd.notna(df["File_Created"]), None)
df["File_Modified"] = df["File_Modified"].where(pd.notna(df["File_Modified"]), None)
df["File_Accessed"] = df["File_Accessed"].where(pd.notna(df["File_Accessed"]), None)

# Database connection parameters
db_params = {
    "dbname": "demo",
    "user": "postgres",
    "password": "pass123#$",
    "host": "localhost",
    "port": "5432"
}

# SQL query for inserting data
insert_query = """
INSERT INTO file_metadata (
    file_path, tags, file_name, file_extension, file_size, 
    file_created, file_modified, file_accessed
) VALUES %s
"""

# Connect to PostgreSQL and insert data
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    values = [
        (
            row["file_path"], 
            row["tags"], 
            row["File_Name"], 
            row["File_Extension"], 
            row["File_Size"],  # Now in KB and integer
            row["File_Created"],
            row["File_Modified"],
            row["File_Accessed"]
        ) for _, row in df.iterrows()
    ]

    execute_values(cursor, insert_query, values)
    conn.commit()

    print("Data inserted successfully!")

except Exception as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()
