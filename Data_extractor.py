import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Retrieve API key securely
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key is missing! Ensure GOOGLE_API_KEY is set in your .env file.")

# Configure Generative AI API
genai.configure(api_key=api_key)

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

# Create the model
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
  system_instruction="Your an advanced Tagger. Your task is to for a given input, you should generate an tag it can be any type of input .i.e image or text.\n\nINCLUDE RARE TAGS SUCH AS NAMES,LOCATIONS,DATES,LINKS\n\nFOR CSV,XML,XLSX FILE INCLUDE ONLY column names\n\n\nexample Output:\n\n{tags:[tag1,tag2,tag3,etc]}\n",
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
  upload_to_gemini("image.png", mime_type="image/png"),
  upload_to_gemini("Kishore_Resume_2.pdf", mime_type="application/pdf"), #upload structure : upload_to_gemini("path to file", mime_type="type/extention")
]

#mime_type = ["image/extension", "video/extention", "audio/extention", "text/extention"]
#for pdfs mime_type = "application/pdf"

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
      ],
    },
    {
      "role": "model",
      "parts": [
        "```json\n{\n\"tags\":[\"puppy\", \"dog\", \"havanese\", \"animal\", \"brown\", \"white\", \"cute\", \"pet\", \"domestic\", \"furry\", \"small dog\", \"sitting\", \"studio shot\", \"canine\", \"mammal\", \"young animal\", \"dog breed\", \"purebred\"]\n}\n```",
      ],
    },
  ]
)

response = chat_session.send_message(files[1]), #user input here

# Extract the first item from the tuple
response = response[0]  

# Extract text from `_result` instead of `result`
if response._result and response._result.candidates:
    generated_text = response._result.candidates[0].content.parts[0].text
    print(generated_text)  # Output the extracted text
else:
    print("No valid response from the model.")
