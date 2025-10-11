from flask import Flask, request, session, render_template
import json
from json_cleaned import json_to_dataframe
import os
import markdown
from supabase import create_client, Client
from dotenv import load_dotenv
from db import add_signup
# IMPORT AT TOP - No more lazy imports!
from new_api import get_top_headlines
from gemini_summarize import get_summary, save_summary_to_gcs
from scrapeResults import get_llm_ready_content

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

file_path = 'news_raw.json'
app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY', 'SUPERSECRETKEY')  # Use env var in production
app.config['SESSION_COOKIE_NAME'] = 'my_session_cookie'

@app.route('/')
def index():
    return render_template('landing_page.html')

@app.route('/index')
def show_form():
    return render_template('index.html')

@app.route('/submit_email', methods=['POST'])
def email_signup():
    session['user_email'] = request.form['chosenEmail']
    user_email = session['user_email']

    session['email_industry'] = request.form['chosenTopic_email']
    email_industry = session['email_industry']

    add_signup(user_email, "Anonymous", email_industry)

    print(f"User email submitted: {user_email}")

    return render_template('thankyou_email.html', user_email=user_email, email_industry=email_industry)

@app.route('/submit_text', methods=['POST'])
def industry_search():
    # Get user input
    session['industry_chosen'] = request.form['chosenTopic']
    session['user_experience_level'] = request.form['experienceLevel']

    # Step 1: Fetch fresh headlines from API
    user_industry_choice = get_top_headlines(session['industry_chosen'])

    # Step 2: Save to JSON file
    with open(file_path, "w") as json_file:
        json.dump(user_industry_choice, json_file, indent=4)
    
    # Step 3: Process JSON into dataframe
    json_to_dataframe(file_path)

    # Step 4: Scrape the URLs from the articles (THIS is what you want to analyze)
    print("Scraping article content...")
    scraped_content = get_llm_ready_content(file_path)
    
    # Step 5: Generate summary from SCRAPED content (not just API response)
    print("Generating AI summary...")
    summary = get_summary(session['user_experience_level'], scraped_content)
    
    # Step 6: Save to GCS
    print("Saving to Google Cloud Storage...")
    gcs_filename = save_summary_to_gcs(summary)
    print(f"Saved to GCS: {gcs_filename}")

    # Step 7: Read and format for display
    with open("summary.txt", "r", encoding="utf-8") as f:
        formatted_summary = f.read()

    formatted_summary = markdown.markdown(formatted_summary)

    # Show results
    return render_template(
        'results.html',
        user_industry_choice=user_industry_choice,
        formatted_summary=formatted_summary,
        industry_chosen=session['industry_chosen'],
        user_experience_level=session['user_experience_level']
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
