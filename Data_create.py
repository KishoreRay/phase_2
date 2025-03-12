import os
import pandas as pd

# Read the CSV file
csv_file = "New_file_tags copy.csv"
df = pd.read_csv(csv_file)

# Extract file details
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

# Apply function to each row
details_df = df["file_path"].apply(get_file_details).apply(pd.Series)

# Merge data and save back to CSV
df = pd.concat([df, details_df], axis=1)

# Remove duplicate columns if they already exist
df = df.loc[:, ~df.columns.duplicated()]

df.to_csv(csv_file, index=False)

print("File metadata extraction completed and saved in", csv_file)
