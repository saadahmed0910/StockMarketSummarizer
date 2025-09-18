from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



def add_signup(email, user_name, industry):
    response = supabase.table("emailsignup").insert({
        "email": email,
        "user_name": user_name,
        "industry": industry
    }).execute()
    return response
