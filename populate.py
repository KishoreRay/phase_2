import pandas as pd
import psycopg2
from datetime import datetime
import json
import os

# PostgreSQL Connection
conn = psycopg2.connect(
    dbname="demo",
    user="postgres",
    password="pass123#$",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
# Read CSV
csv_file = "New_file_tags copy.csv"

df = pd.read_csv(csv_file)

# Fix "tags" column: Convert Python-like set to valid JSON array
def fix_tags(value):
    if pd.isna(value) or value == "{}":  # Handle empty values
        return None
    try:
        tags_list = list(eval(value))  # Convert string to Python set, then list
        return json.dumps(tags_list)   # Convert list to valid JSON string
    except:
        return None  # If parsing fails, return None

df["tags"] = df["tags"].apply(fix_tags)

# Convert "NaN" in timestamps & file_size to None
timestamp_cols = ["File_Created", "File_Modified", "File_Accessed"]
for col in timestamp_cols:
    df[col] = df[col].apply(lambda x: None if pd.isna(x) else x)

# Convert file_size from bytes to KB (rounded)
df["File_Size"] = df["File_Size"].apply(lambda x: int(round(x / 1024)) if not pd.isna(x) and x > 0 else 0)

# Extract file_name from file_path if missing
df["File_Name"] = df.apply(lambda row: os.path.basename(row["file_path"]) if pd.isna(row["File_Name"]) else row["File_Name"], axis=1)

# Extract file extension from file_name
df["File_Extension"] = df["File_Name"].apply(lambda x: os.path.splitext(x)[1] if pd.notna(x) else "")


# Insert data
insert_query = """
INSERT INTO file_metadata (file_path, tags, file_name, file_extension, file_size, file_created, file_modified, file_accessed)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

# Convert DataFrame to list of tuples
data = df.where(pd.notna(df), None).to_records(index=False).tolist()

# Execute batch insert
cursor.executemany(insert_query, data)
conn.commit()

print("Data inserted successfully!")

# Close connection
cursor.close()
conn.close()