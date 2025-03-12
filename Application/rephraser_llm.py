import os
from dotenv import load_dotenv
import google.generativeai as genai
from Query_runner import get_result

# Load environment variables from .env
load_dotenv()

# Retrieve API key securely
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key is missing! Ensure GOOGLE_API_KEY is set in your .env file.")

# Configure Generative AI API
genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="Your simple SQL response rephraser. Your task is to rephrase the OUTPUT from SQL DATABASE into an Natural Language Response. understandable by user.\ngive paths in seperate line. \n. give paths in seperate line.\n give the response in markdown.\n user_query=",
)

chat_session = model.start_chat(
  history=[
  ]
)
def rephraser(user_query):
    result = get_result(user_query)
    result2 = result
    result = str(result)
    #print(result)
    response = chat_session.send_message(user_query + "\n" + "search result= "+ "\n" +result)
    return result2,response.text

out1,out2 = rephraser("show me all images realted ichigo from bleach")
print(out1)
print(out2)

