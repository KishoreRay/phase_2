# filepath: /e:/phase_2/Application/sync.py
import os
import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm
from knowledge_builder import scan_and_generate_tags  # Import the function to generate tags

def scan_drives(scan_paths):
    new_files = []
    for path in scan_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                # Check if the file is new (you can implement your own logic here)
                if is_new_file(file_path):
                    new_files.append({"file_path": file_path, "tags": "[]"})  # Add default tags or modify as needed
    return new_files

def is_new_file(file_path):
    # Implement your logic to determine if the file is new
    # For example, you can check the file creation date or maintain a record of processed files
    return True

def create_new_files_csv(new_files, csv_file):
    df = pd.DataFrame(new_files)
    df.to_csv(csv_file, index=False)
    print(f"New files CSV created: {csv_file}")

def extract_file_details(csv_file, output_csv_file):
    df = pd.read_csv(csv_file)

    def get_file_details(file_path):
        try:
            file_stats = os.stat(file_path)
            return {
                "File_Name": os.path.basename(file_path),
                "File_Extension": os.path.splitext(file_path)[1],
                "File_Size": file_stats.st_size,  # bytes
                "File_Created": pd.to_datetime(file_stats.st_ctime, unit='s'),
                "File_Modified": pd.to_datetime(file_stats.st_mtime, unit='s'),
                "File_Accessed": pd.to_datetime(file_stats.st_atime, unit='s')
            }
        except FileNotFoundError:
            return {
                "File_Name": None,
                "File_Extension": None,
                "File_Size": None,
                "File_Created": None,
                "File_Modified": None,
                "File_Accessed": None
            }

    details_df = df["file_path"].apply(get_file_details).apply(pd.Series)
    df = pd.concat([df, details_df], axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    df.to_csv(output_csv_file, index=False)
    print(f"File metadata extraction completed and saved in {output_csv_file}")

def populate_database(csv_file):
    df = pd.read_csv(csv_file)

    df["tags"] = df["tags"].apply(lambda x: json.dumps(x.split(", ")) if pd.notna(x) else "[]")
    df["File_Size"] = df["File_Size"].fillna(0).astype(float) / 1024  # Convert bytes to KB
    df["File_Size"] = df["File_Size"].astype(int)  # Ensure integer values
    df["File_Created"] = df["File_Created"].where(pd.notna(df["File_Created"]), None)
    df["File_Modified"] = df["File_Modified"].where(pd.notna(df["File_Modified"]), None)
    df["File_Accessed"] = df["File_Accessed"].where(pd.notna(df["File_Accessed"]), None)

    db_params = {
        "dbname": "demo",
        "user": "postgres",
        "password": "pass123#$",
        "host": "localhost",
        "port": "5432"
    }

    insert_query = """
    INSERT INTO file_metadata (
        file_path, tags, file_name, file_extension, file_size, 
        file_created, file_modified, file_accessed
    ) VALUES %s
    ON CONFLICT (file_path) DO UPDATE SET
        tags = EXCLUDED.tags,
        file_name = EXCLUDED.file_name,
        file_extension = EXCLUDED.file_extension,
        file_size = EXCLUDED.file_size,
        file_created = EXCLUDED.file_created,
        file_modified = EXCLUDED.file_modified,
        file_accessed = EXCLUDED.file_accessed
    """

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

        print("Data inserted/updated successfully!")

    except Exception as e:
        print("Error:", e)

    finally:
        cursor.close()
        conn.close()

def syncer(scan_paths):
    # Generate tags and create temp_file_tags.csv
    scan_and_generate_tags(scan_paths, "temp_file_tags.csv")

    # Read the generated CSV file
    new_files = pd.read_csv("temp_file_tags.csv").to_dict('records')
    if new_files:
        create_new_files_csv(new_files, "NEW_FILES.CSV")
        extract_file_details("NEW_FILES.CSV", "NEW_FILES_DATA.CSV")
        populate_database("NEW_FILES_DATA.CSV")
    else:
        print("No new files found.")

if __name__ == "__main__":
    SCAN_DRIVES = ["E:\\new_file_test"]  # Update with actual paths to scan
    syncer(SCAN_DRIVES)