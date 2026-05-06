import pandas as pd
import gspread
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. Load hidden passwords from the .env file
load_dotenv()


SHEET_URL = 'https://docs.google.com/spreadsheets/d/1slhkIRVPeEZyCPJzfbb4Hs7QBH-QTlCsrgLDPaDJY0E/edit'
DB_URI = os.getenv("DB_URI") 

def run_sync():
    print("1. Connecting to Google Sheets...")
    # Requires google_secret.json to be in the same folder
    gc = gspread.service_account(filename='google_secret.json')
    sheet = gc.open_by_url(SHEET_URL).sheet1
    data = sheet.get_all_records()
    
    df = pd.DataFrame(data)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    print(f"   -> Pulled {len(df)} rows.")

    print("\n2. Pushing to Supabase (PostgreSQL)...")
    engine = create_engine(DB_URI)
    df.to_sql('alumni_records', engine, if_exists='replace', index=False)
    
    print("\n✅ Success! Database is live and updated.")

if __name__ == "__main__":
    run_sync()

