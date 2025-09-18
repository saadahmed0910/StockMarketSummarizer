from flask import Flask, request, session, render_template
import json
from json_cleaned import json_to_dataframe
import os
import markdown
from supabase import create_client, Client
from dotenv import load_dotenv
from db import add_signup

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



file_path = 'news_raw.json'
app = Flask(__name__)

app.secret_key = 'SUPERSECRETKEY'
app.config['SESSION_COOKIE_NAME'] = 'my_session_cookie'

@app.route('/')
def index():
    # Show the input form to the user
    return render_template('index.html')

@app.route('/submit_email', methods=['POST'])
def email_signup():
    # Only triggered when user submits the form
    session['user_email'] = request.form['chosenEmail']
    user_email = session['user_email']

    session['email_industry'] = request.form['chosenTopic_email']
    email_industry = session['email_industry'] #redundant but whatever

    add_signup(user_email, "Anonymous", email_industry)  # Save to Supabase

    print(f"User email submitted: {user_email}")  # Debugging line to confirm email capture

    # Acknowledge email submission
    return render_template('thankyou_email.html', user_email=user_email, email_industry=email_industry)



@app.route('/submit_text', methods=['POST'])
def industry_search():
    from new_api import get_top_headlines
    
    # Only triggered when user submits the form
    session['industry_chosen'] = request.form['chosenTopic']
    session['user_experience_level'] = request.form['experienceLevel']

    # Fetch fresh headlines
    user_industry_choice = get_top_headlines(session['industry_chosen'])

    # Save fresh data to JSON file
    with open(file_path, "w") as json_file:
        json.dump(user_industry_choice, json_file, indent=4)
    
    json_to_dataframe(file_path)  # Process the fresh JSON data

    from gemini_summarize import get_summary, save_summary_to_gcs #Import here to avoid error on loading this before df is created
    # Generate summary based on fresh input
    summary = get_summary(session['user_experience_level'], user_industry_choice)
    save_summary_to_gcs(summary)


    with open("summary.txt", "r", encoding="utf-8") as f:
        formatted_summary = f.read() #stored results in summary.txt and am reading from there

    formatted_summary = markdown.markdown(formatted_summary)

    # Show results
    return render_template(
        'results.html',
        user_industry_choice=user_industry_choice,
        formatted_summary=formatted_summary
    )




if __name__ == '__main__':
    app.run(debug=True)