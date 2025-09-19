import json
import pandas as pd
import os

# Define the file path
file_path = os.path.join(os.getcwd(), "news_raw.json")

def json_to_dataframe(file_path):
    # Use a default file path if none is provided
    if file_path is None:
        file_path = os.path.join(os.getcwd(), "news_raw.json")
        
    # Check if the file exists; if not, create it
    if not os.path.exists(file_path):
        print(f"File not found: '{file_path}'. Creating a new empty JSON file.")
        try:
            with open(file_path, 'w') as f:
                json.dump({'articles': []}, f)
        except IOError as e:
            print(f"Error creating file: {e}")
            return None
    

    # Step 1: Open the JSON file and load the data
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        
        # Check if the 'articles' key exists and contains a list
        if 'articles' in data and isinstance(data['articles'], list):
            articles_list = data['articles']
            
            # Step 2: Use json_normalize to flatten the data into a DataFrame
            # This single line handles the entire conversion
            df = pd.json_normalize(articles_list)

            # Create a database connection to a new SQLite database file
            print(df.head())
        
        else:
            print("Error: 'articles' key not found or is not a list in the JSON file.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Please check the file's format.")

    return df

