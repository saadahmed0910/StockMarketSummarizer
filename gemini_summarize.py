from google import genai
import requests
from tqdm import tqdm
import time
from dotenv import load_dotenv
from scrapeResults import llm_ready_content
import os
import json
from google.cloud import storage
from datetime import datetime
import uuid
from google.oauth2 import service_account



load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
client = genai.Client()

def get_summary(experience_level, content):
    # Improved prompt with clearer instructions and formatting examples
    with open("example_format.txt", "r", encoding="utf-8") as f:
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
        {llm_ready_content}
        """)

    with open("summary.txt", "w", encoding="utf-8") as f:
        f.write(response.text)

    return response.text



def save_summary_to_gcs(summary):
    creds = service_account.Credentials.from_service_account_file(
        "/Users/saada/Desktop/AI Project 1/financial-market-projects-5752586a7e64.json"
    )
    storage_client = storage.Client(credentials=creds)
    bucket = storage_client.bucket("marketanalyzerproject")

    random_id = str(uuid.uuid4())
    filename = f"summaries/{random_id}.md"

    blob = bucket.blob(filename)
    blob.upload_from_string(summary, content_type="text/markdown")

    return filename












