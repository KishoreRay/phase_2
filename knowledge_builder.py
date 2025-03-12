import os
import csv
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Retrieve API key securely
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key is missing! Ensure GOOGLE_API_KEY is set in your .env file.")

# Configure Generative AI API
genai.configure(api_key=api_key)

# Gemini model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}


model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="Your task is to generate tags for any input file. "
                       "Include rare tags like names, locations, dates, and links.\n "
                       "If its a documnet then generat tags on what the document is about,what are the key topics,imagine additional possible tags from existing ones\n\n"
                       "If image,or video then generate tags on what the image is about imagine additional possible tags from existing ones\n"
                       "For CSV, XML, and XLSX files, include only column names.\n\n"
                       "Extract all tags in lower case\n\n"
                       "IF Code file then generate tags for the code,whats the code about,functions,libraries used\n\n"
                       "If there is of more than 1 word in a single tag. then additionaly make the other words as seperate tags\n\n"
                       "Example Output:\n"
                       "{tags:[tag1, tag2, tag3, ...]}\n",
)


SCAN_DRIVES = [#"C:\\Users\\Kishore\\Downloads",
               "C:\\Users\\Kishore\\OneDrive - Amrita Vishwa Vidyapeetham- Chennai Campus\\Documents\\Resumes",
               "D:\\clg sem 3"
               "D:\\clg sem5",
               "D:\\LLM",
               "D:\\sem4",
               "E:\\7thsem",
               "E:\\datasets_metanomos_backend",
               "E:\\Derisk360",
               "E:\\images",
               "E:\\movies",
               #"E:\\networks_lab",
               "E:\\New folder (2)",
               "E:\\pdfs1",
               "E:\\pdfs2",
               "E:\\Phase_1",
               "E:\\poc",
               "E:\\Untitled Folder",
               ]  # Change this to the drives/folders you want to scan

OUTPUT_CSV = "temp_file_tags.csv"


SUPPORTED_EXTENSIONS = {
    ".txt", ".csv",".pdf", ".jpg", ".png", ".mp4",
    ".py", ".html", ".java", ".cpp", ".mp3", ".wav"  # Newly added
}

SKIP_FOLDERS = {"C:\\Users\\Kishore\\.anaconda\\",
                "C:\\Users\\Kishore\\venv",
                "C:\\Users\\Kishore\\anaconda3\\",
                "C:\\Users\\\Kishore\\AppData\\",
                 "C:\\Users\\Kishore\\.cache\\",
                 "C:\\Users\\Kishore\\.cache\\",
                 "C:\\Users\\Kishore\\.conda\\",
                 "C:\\Users\\Kishore\\.config\\",
                 "C:\\Users\\Kishore\\.continuum\\",
                 "C:\\Users\\Kishore\\.deepface\\",
                 "C:\\Users\\Kishore\\.docker\\",
                 "C:\\Users\\Kishore\\.dotnet\\",
                 "C:\\Users\\Kishore\\.EasyOCR\\",
                 "C:\\Users\\Kishore\\.insomniac\\",
                 "C:\\Users\\Kishore\\.ipynb_checkpoints\\",
                 "C:\\Users\\Kishore\\.ipython\\",
                 "C:\\Users\\Kishore\\.jdks\\",
                 "C:\\Users\\Kishore\\.jupyter\\",
                 "C:\\Users\\Kishore\\.keras\\",
                 "C:\\Users\\Kishore\\.m2\\",
                 "C:\\Users\\Kishore\\.matplotlib\\",
                 "C:\\Users\\Kishore\\.templateengine\\",
                 "C:\\Users\\Kishore\\.thumbnails\\",
                 "C:\\Users\\Kishore\\.Neo4jDesktop\\",
                 "C:\\Users\\Kishore\\.nuget\\packages\\",
                 "C:\\Users\\Kishore\\anaconda3\\",
                 "C:\\Users\\Kishore\\ansel\\",
                 "C:\\Users\\Kishore\\blenderkit_data\\",
                 "C:\\Users\\Kishore\\Cisco Packet Tracer 8.2.1\\",
                 "C:\\Users\\Kishore\\.VirtualBox\\",
                 "C:\\Users\\Kishore\\.vscode\\",
                 "C:\\Users\\Kishore\\Cisco Packet Tracer 8.2.1\\",
                 "D:\\3.5",
                 "D:\\blender.crt\\",
                 "D:\\blender.shared\\",
                 "D:\\Cisco Packet Tracer 8.2.1\\",
                 "D:\\Drivers\\",
                 "D:\\Export dsch2\\",
                 "D:\\Games\\",
                 "D:\\Kali_x64\\",
                 "D:\\license\\",
                 "D:\\New folder (2)\\",
                 "D:\\Wuthering Waves\\",
                 "E:\\3uTools\\",
                 "E:\\AMAZON_ML\\",
                 "E:\\Blender\\",
                 "E:\\Epic Games\\",
                 "E:\\fall guys\\",
                 "E:\\games\\",
                 "E:\\gms\\",
                 "E:\\hallofhacks\\",
                 "E:\\intellij\\",
                 "E:\\Java\\",
                 "E:\\java_21\\",
                 "E:\\metanomos\\.venv",
                 "E:\\neo4j\\",
                 "E:\\Oracle\\",
                 "E:\\SOMEFOLDER\\",
                 "E:\\UE_5.1\\",
                 "E:\\Untitled Folder\\New folder (2)\\",
                 "E:\\vidut\\",
                 "E:\\Wonderla\\",
                 }


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini and returns the uploaded file object."""
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Upload failed for {path}: {e}")
        return None


def wait_for_files_active(files):
    """Waits for the given files to become ACTIVE before proceeding."""
    print("Waiting for file processing...")
    for file in files:
        while True:
            file_info = genai.get_file(file.name)
            state = file_info.state.name
            if state == "ACTIVE":
                print(f"File {file.name} is now active and ready for processing.")
                break
            elif state == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)  # Wait before checking again
            else:
                raise Exception(f"File {file.name} failed to process with state: {state}")
    print("\nAll files are ready.\n")


def process_file(file_path, writer, existing_files):
    """Processes a single file: uploads, extracts tags, and writes to CSV."""
    if file_path in existing_files:
        print(f"Skipping already processed file: {file_path}")
        return

    # Determine MIME type
    ext = os.path.splitext(file_path)[-1].lower()
    mime_types = {
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".xml": "text/xml",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".json": "text/plain",  # JSON is handled as text instead of uploading as a file
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".mp4": "video/mp4",
    # Newly added file types
    ".py": "text/plain",      # Python scripts are text-based
    ".html": "text/html",      # HTML files are text-based
    ".java": "text/plain",     # Java source code is text-based
    ".cpp": "text/plain",      # C++ source code is text-based
    ".mp3": "audio/mpeg",      # MP3 audio format
    ".wav": "audio/wav"        # WAV audio format
}
    mime_type = mime_types.get(ext)
    if not mime_type:
        print(f"Skipping unsupported file type: {file_path}")
        return

    # Upload the file
    file_obj = upload_to_gemini(file_path, mime_type=mime_type)
    if not file_obj:
        return

    # Wait until the file is ACTIVE
    wait_for_files_active([file_obj])

    # Upload an example file for context (ensure this file exists)
    example_file = upload_to_gemini("image.png", mime_type="image/png")
    wait_for_files_active([example_file])

    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [example_file]},
            {"role": "model", "parts": ["```json\n{\n\"tags\":[\"puppy\", \"dog\", \"havanese\", \"animal\", \"brown\", \"white\", \"cute\", \"pet\", \"domestic\", \"furry\", \"small dog\", \"sitting\", \"studio shot\", \"canine\", \"mammal\", \"young animal\", \"dog breed\", \"purebred\"]\n}\n```"]},
        ]
    )

    # Send actual file for tagging
    response = chat_session.send_message(file_obj)
    if response and response.candidates:
        generated_text = response.candidates[0].content.parts[0].text
  # Extract tuple first item

    if response._result and response._result.candidates:
        generated_text = response._result.candidates[0].content.parts[0].text
        print(f"Raw API Response for {file_path}: {generated_text}")

        try:
            tags = eval(generated_text).get("tags", [])
            writer.writerow([file_path, ", ".join(tags)])
            print(f"Processed: {file_path} -> Tags: {tags}")
        except Exception as e:
            print(f"Error parsing response for {file_path}: {e}")
    else:
        print(f"No valid response for {file_path}")


def scan_and_generate_tags():
    """Scans files, extracts tags using Gemini, and writes to CSV."""
    existing_files = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, mode="r", encoding="utf-8") as f:
            existing_files = {row[0] for row in csv.reader(f)}

    with open(OUTPUT_CSV, mode="w" if not existing_files else "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not existing_files:
            writer.writerow(["file_path", "tags"])  # Write header

        print("Starting file scan...")

        for drive in SCAN_DRIVES:
            print(f"Scanning: {drive}")
            for root, _, files in os.walk(drive):
                if any(os.path.commonpath([root, skip_folder]) == skip_folder for skip_folder in SKIP_FOLDERS if os.path.splitdrive(root)[0] == os.path.splitdrive(skip_folder)[0]):
                    print(f"Skipping folder: {root}")
                    continue

                for file in files:
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[-1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        print(f"Processing file: {file_path}")
                        process_file(file_path, writer, existing_files)
                        csvfile.flush()  # Ensure data is written immediately

    print("File scanning complete!")


if __name__ == "__main__":
    scan_and_generate_tags()
