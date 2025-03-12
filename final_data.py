import pandas as pd

# Load CSV file
df = pd.read_csv("file_tags copy.csv")

# Function to convert tags into JSONB format
def convert_to_jsonb(value):
    if pd.isna(value):  # Handle NaN values
        return "{}"
    if isinstance(value, (int, float)):  # Handle numeric values
        return f'{{"{value}"}}'
    tags = [f'"{tag.strip()}"' for tag in str(value).split(",")]
    return "{" + ", ".join(tags) + "}"

# Apply transformation to the 'tags' column
df["tags"] = df["tags"].apply(convert_to_jsonb)

# Save the modified DataFrame back to CSV
df.to_csv("modified_file.csv", index=False)

print("CSV file updated successfully!")
