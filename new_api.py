from newsapi import  NewsApiClient
from datetime import datetime, timedelta, date


import os
from dotenv import load_dotenv

load_dotenv()

newsapikey = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(newsapikey)

today = date.today()
yesterday = today - timedelta(days = 1)
day_before_yesterday = today - timedelta(days = 2)

def get_top_headlines(choice):

    top_headlines = newsapi.get_everything(q = str(choice), # keywords or phrase to search for
                                            language='en',
                                            from_param = (day_before_yesterday),
                                            to = (yesterday),
                                            sort_by = 'relevancy',
                                            page_size = 15
                                            )
                                            
    

    return top_headlines

