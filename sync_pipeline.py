import pandas as pd
import gspread
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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

    print("\n2. Geocoding Locations...")
    geolocator = Nominatim(user_agent="phm_alumni_pipeline")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    # Check if 'location' column exists
    if 'location' in df.columns:
        unique_locs = df['location'].dropna().unique()
        coords = {}
        for loc in unique_locs:
            try:
                location = geocode(f"{loc}, USA")
                coords[loc] = (location.latitude, location.longitude) if location else (None, None)
            except:
                coords[loc] = (None, None)
        
        df['latitude'] = df['location'].map(lambda x: coords.get(x, (None, None))[0])
        df['longitude'] = df['location'].map(lambda x: coords.get(x, (None, None))[1])
        print("   -> Coordinates mapped successfully.")
    else:
        print("   -> No 'location' column found. Skipping geocoding.")

    print("\n3. Pushing to Supabase (PostgreSQL)...")
    engine = create_engine(DB_URI)
    df.to_sql('alumni_records', engine, if_exists='replace', index=False)
    
    print("\n✅ Success! Database is live and updated.")

if __name__ == "__main__":
    run_sync()

