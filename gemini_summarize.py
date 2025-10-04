from google import genai
from tqdm import tqdm
from dotenv import load_dotenv
from scrapeResults import get_llm_ready_content
import os
from google.cloud import storage
from datetime import datetime
import uuid
from google.oauth2 import service_account

load_dotenv()

# DEBUG - Remove this after it works
print("="*50)
print("Environment Variables Check:")
print(f"GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"GCS_KEY_FILE: {os.getenv('GCS_KEY_FILE')}")
print(f"GCS_CREDENTIALS_PATH: {os.getenv('GCS_CREDENTIALS_PATH')}")
print("="*50)






os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
client = genai.Client()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
example_format_path = os.path.join(BASE_DIR, "example_format.txt")

def get_summary(experience_level, content):
    # Improved prompt with clearer instructions and formatting examples
    with open(example_format_path, "r", encoding="utf-8") as f:
        example_format = f.read()

        # Assuming your scraped article content is stored in this variable

    # Your API call with the improved prompt as an f-string
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=
                    f"""
        You are an expert market analyst whose goal is to provide a comprehensive analysis of the following news articles to help an individual understand key market factors. 
        Your analysis must not provide financial advice, but rather contextualize the news within the relevant market.

        **Instructions:**
        1. Filter out any articles or information that is not significant to market chosen which is {content}. Focus only on content that could meaningfully impact a company's stock, an industry, or investor sentiment.  

        2. For each relevant article please refer to {example_format} for the formatting structure that must strictly be followed.

        3. After analyzing all articles, provide a final section titled:

        ### Overall Market Summary
        Write a 3 to 5 sentence synthesis summarizing the key themes across all articles, highlighting broad opportunities, risks, or macroeconomic implications.

        Remember the experience level of the user is {experience_level}. Tailor your language and explanations accordingly, avoiding jargon for beginners and providing deeper insights for advanced users.
        
        Here is the content of the articles:
        {content}
        """)
    
    summary_path = os.path.join(os.getcwd(), "summary.txt")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    return response.text

def save_summary_to_gcs(summary):
    gcs_key_path = os.getenv('GCS_CREDENTIALS_PATH')
    creds = service_account.Credentials.from_service_account_file(
        gcs_key_path
    )
    storage_client = storage.Client(credentials=creds)
    bucket = storage_client.bucket("marketanalyzerproject")

    random_id = str(uuid.uuid4())
    filename = f"summaries/{random_id}.md"

    blob = bucket.blob(filename)
    blob.upload_from_string(summary, content_type="text/markdown")

    return filename












