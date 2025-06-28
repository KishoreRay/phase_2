# Context Aware Tag Based File Search Using LLMs

## Overview
This project is a file search system that allows users to search for files based on natural language queries. The system extracts metadata from files, stores them in a PostgreSQL database, and uses a generative AI model to convert user queries into SQL queries. The results are then rephrased into a human-readable format.

## Features
- **File Metadata Extraction**: Extracts file name, extension, size, created/modified timestamps, and auto-generates tags using generative AI.
- **Database Storage**: Stores metadata in a PostgreSQL database.
- **Natural Language Query Processing**: Uses a generative AI model to convert user queries into SQL queries.
- **File Preview & Open Support**: Provides previews for images, PDFs, and text-based files.
- **Rephrased Responses**: AI-generated responses make search results user-friendly.
- **Sync Mechanism**: Scans and updates the database with new files dynamically.

## Technologies Used
- **Python**: Core programming language.
- **PostgreSQL**: Stores file metadata.
- **Streamlit**: Web-based UI for interaction.
- **Google Gemini AI**: Used for query generation and rephrasing.
- **PyMuPDF**: PDF processing.
- **Pandas**: Data manipulation.
- **psycopg2**: PostgreSQL connection.
- **dotenv**: For managing API keys securely.

## Project Structure
```
📂 Application
│── app.py               # Streamlit UI for chat and file search
│── sync.py              # Scans and updates file metadata
│── knowledge_builder.py # Generates tags using AI for file classification
│── Query_generator.py   # Converts natural language queries into SQL
│── Query_runner.py      # Executes generated SQL queries
│── rephraser_llm.py     # Rephrases search results into readable format
│── Data_create.py       # Extracts file details and prepares CSV
│── .env                 # Stores API keys securely
```

## Installation
### Prerequisites
- Python 3.8+
- PostgreSQL installed and configured
- API Key for Google Gemini AI (set in `.env` file)

### Steps
1. **Clone the repository**
   ```sh
   git clone <repo_url>
   cd project_root
   ```
2. **Create a virtual environment** (optional but recommended)
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. **Set up `.env` file**
   ```sh
   echo "GOOGLE_API_KEY=your_api_key" > .env
   ```
4. **Initialize the database**
   - Create a PostgreSQL database named `demo`.
   - Create the `file_metadata` table using:
   ```sql
   CREATE TABLE file_metadata (
       id SERIAL PRIMARY KEY,
       file_path TEXT NOT NULL,
       tags JSONB,
       file_name TEXT NOT NULL,
       file_extension TEXT NOT NULL,
       file_size BIGINT,
       file_created TIMESTAMP,
       file_modified TIMESTAMP,
       file_accessed TIMESTAMP
   );
   ```
5. **Change the scan folder in knowledge_builder.py and Application/Sync.py as per requirement ***

6. **Run the application**
   ```sh
   streamlit run app.py
   ```

## Usage
- The UI provides a search bar where users can enter natural language queries.
- Example queries:
  - "Find my resume."
  - "Show me the PDF files related to machine learning."
  - "Where are the videos from my vacation?"
- The system retrieves matching files and displays them with previews.

## Future Enhancements
- individul object detection within an video make more diverse searching.
- Improve query understanding using RAG-based retrieval models.
- Expand supported file formats.


