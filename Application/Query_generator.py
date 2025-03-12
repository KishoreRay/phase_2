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

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

#model = genai.GenerativeModel(
 # model_name="gemini-1.5-flash-8b",
 # generation_config=generation_config,
 # system_instruction="Yout an advanced PGSQL query generator. Your task is to generate PGSQL Query based user query.\nUse the below table Schema to generate pqsql query. the user query might look not same as interacting with database instead look like asking an file related query in natural language \n\nConstraints:\nMust only generate query and no other output is allowed\n\nTable Name: file_metadata\n\nTable Schema://\n______________________________________________________________________________________________________________\n|   column_name    |          data_type                             |   is_nullable                  |               column_default                              |\n|------------------|-------------------------------|----------------------|----------------------------------------|\n| id                            | integer                                           | NO                                 | nextval('file_metadata_id_seq'::regclass)   |\n| file_path                | text                                                 | NO                                 | null                                        |\n| tags                        | jsonb                                              | YES                                | null                                        |\n| file_name               | text                                                | NO                                 | null                                        |\n| file_extension        | text                                                | NO                                 | null                                        |\n| file_size                  | bigint                                             | YES                                | null                                        |\n| file_created           | timestamp without time zone    | YES                                | null                                        |\n| file_modified         | timestamp without time zone    | YES                               | null                                        |\n| file_accessed        | timestamp without time zone   | YES                                | null                                        |\n--------------------------------------------------------------------------------------------------------------\n\n//\n\n\n\nQuery Generation Hints:\n-imagine other possible keywords that can be additionally created from user query. \n-Extract all possible tags from the user query.\n-File extension always starts with \".\"\n-File_size is stored in KB.\n-Always use tags to search.\n-think of possible file formats for user query.\n-generate query only for required data.\n-jsonb store in \"[]\" .\n-USE OR operator between 2 tags if using  multiple keywords.\nex: \"rosewater\",\"rose\",\"water\"\n-all tags in only smaller case.\n\nEXAMPLE:\nuser: show me the image i took with my friends in theme park\nAi: SELECT\n  file_path,\n  file_name,\n  file_extension\nFROM\n  file_metadata\nWHERE\n  tags @> '[\"theme park\"]' OR tags @> '[ \"friends\"]' OR   tags @> '[\"park\"]' OR   tags @> '[\"amusement park\"]'\n  AND file_extension LIKE '%.jpg'\n  OR file_extension LIKE '%.jpeg'\n  OR file_extension LIKE '%.png'\nLIMIT 10;\n",
#)
with open(r"E:\phase_2\prompt_template.jinja", "r", encoding="utf-8") as file:
    jinja_template = file.read()

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="\nYout an advanced PGSQL query generator. Your task is to generate PGSQL Query based user query.\nUse the below table Schema to generate pqsql query. the user query might look not same as interacting with database instead look like asking an file related query in natural language \n\nConstraints:\nMust only generate query and no other output is allowed\n\nTable Name: file_metadata\n\nTable Schema://\n______________________________________________________________________________________________________________\n|   column_name    |          data_type                             |   is_nullable                  |               column_default                              |\n|------------------|-------------------------------|----------------------|----------------------------------------|\n| id                            | integer                                           | NO                                 | nextval('file_metadata_id_seq'::regclass)   |\n| file_path                | text                                                 | NO                                 | null                                        |\n| tags                        | jsonb                                              | YES                                | null                                        |\n| file_name               | text                                                | NO                                 | null                                        |\n| file_extension        | text                                                | NO                                 | null                                        |\n| file_size                  | bigint                                             | YES                                | null                                        |\n| file_created           | timestamp without time zone    | YES                                | null                                        |\n| file_modified         | timestamp without time zone    | YES                               | null                                        |\n| file_accessed        | timestamp without time zone   | YES                                | null                                        |\n--------------------------------------------------------------------------------------------------------------\n\n//\n\n\n\nQuery Generation Hints:\n\n-imagine possible keywords that can be additionally formed from user query. \nex: actual:rose, imagined: \"red\",\"flower\",\"roses\",\"plants\"\n-Extract all possible tags from the user query.\n-File extension always starts with \".\"\n-File_size is stored in KB.\n-Always use tags to search.\n-think of possible file formats for user query.\n-generate query only for required data.\n-jsonb store in \"[]\" .\n-USE OR operator between 2 tags if using  multiple keywords.\nex: \"rosewater\",\"rose\",\"water\"\n\n-all tags in only smaller case.\n\nMUST FOLLOW:\n-Always use parentheses to explicitly group AND and OR conditions to ensure correct evaluation order.\nex:\nWHERE (A OR B) AND (C)\n\n-If a condition involves multiple ORs, wrap them in parentheses before applying AND.\n-Ensure that filters are logically grouped to prevent unintended behavior.\n",
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "find where the video i took in karthik concert?\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT\n  file_path,\n  file_name,\n  file_extension\nFROM\n  file_metadata\nWHERE\n  (tags @> '[\"karthik concert\"]' OR tags @> '[\"concert\"]' OR tags @> '[\"karthik\"]')\n  AND file_extension LIKE '%.mp4'\n  OR file_extension LIKE '%.mov'\n;\n```\n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "find documents related to Support Vector Classification",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT\n  file_path,\n  file_name,\n  file_extension\nFROM\n  file_metadata\nWHERE\n  (\n    tags @> '[\"support vector classification\"]' OR tags @> '[\"support vector machine\"]' OR tags @> '[\"classification\"]'\n  )\n  AND (\n    file_extension LIKE '%.pdf'\n    OR file_extension LIKE '%.txt'\n    OR file_extension LIKE '%.docx'\n    OR file_extension LIKE '%.doc'\n  );\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "list all images related to cars",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT\n  file_path,\n  file_name,\n  file_extension\nFROM\n  file_metadata\nWHERE\n  (tags @> '[\"cars\"]' OR tags @> '[\"car\"]')\n  AND (\n    file_extension LIKE '%.jpg'\n    OR file_extension LIKE '%.jpeg'\n    OR file_extension LIKE '%.png'\n    OR file_extension LIKE '%.gif'\n    OR file_extension LIKE '%.bmp'\n  );\n```",
      ],
    },
    {
      "role": "user",
      "parts": [
        "list pdf of related to llm\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "```sql\nSELECT\n  file_path,\n  file_name,\n  file_extension\nFROM\n  file_metadata\nWHERE\n  (tags @> '[\"llm\"]' OR tags @> '[\"large language model\"]')\n  AND file_extension LIKE '%.pdf';\n```",
      ],
    },
  ]
)

def get_query(user_query):
    response = chat_session.send_message(user_query)
    
    # Extract the text from response (assuming it's stored in .text or another attribute)
    query_text = response.text if hasattr(response, "text") else str(response)
    
    # Remove SQL markdown formatting
    query_text = query_text.strip("```sql").strip()

    query_text = query_text.strip(";\n```").strip()

    #print(query_text)
    
    return query_text+";"

#sample = get_query("how many images are there related to rose?")
#print(sample)  # No need for .text since it's now a string
