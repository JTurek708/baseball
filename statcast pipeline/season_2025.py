import io
import pandas as pd
from datetime import datetime, timedelta
from pybaseball import statcast
from google.cloud import storage

def run_pipeline_for_yesterday(bucket_name: str, master_filename: str = "master2025.csv"):
    # 1. Calculate yesterday's date
    yesterday = datetime.today() - timedelta(days=1)
    formatted_date = yesterday.strftime("%Y-%m-%d")
    print(f"Processing data for {formatted_date}...")
    
    # 2. Only process if yesterday is on/after the season start (March 18, 2025)
    season_start = datetime(2025, 3, 17)
    if yesterday < season_start:
        print(f"Yesterday ({formatted_date}) is before season start ({season_start.strftime('%Y-%m-%d')}). Skipping.")
        return
    
    # 3. Retrieve the day's data using pybaseball
    try:
        data = statcast(start_dt=formatted_date, end_dt=formatted_date)
    except Exception as e:
        print(f"Error retrieving data for {formatted_date}: {e}")
        return
    
    if data.empty:
        print(f"No data retrieved for {formatted_date}.")
        return
    
    print(f"Retrieved {len(data)} rows of data for {formatted_date}.")
    
    # 4. Initialize the Cloud Storage client and target bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    master_blob = bucket.blob(master_filename)
    
    # 5. Download the existing master CSV (if it exists) and append the new data
    try:
        master_csv_contents = master_blob.download_as_string().decode("utf-8")
        master_df = pd.read_csv(io.StringIO(master_csv_contents))
        print("Existing master file found. Appending new data.")
        combined_df = pd.concat([master_df, data], ignore_index=True)
    except Exception as e:
        # If the file does not exist or cannot be read, start with today's data
        print("Master file not found or error reading it; creating a new master file.")
        combined_df = data

    # 6. Convert the combined DataFrame to CSV (in-memory) and upload it
    combined_csv_buffer = io.StringIO()
    combined_df.to_csv(combined_csv_buffer, index=False)
    combined_csv_contents = combined_csv_buffer.getvalue()
    master_blob.upload_from_string(combined_csv_contents, content_type="text/csv")
    print(f"Master CSV file successfully updated in bucket '{bucket_name}' as '{master_filename}'.")

if __name__ == "__main__":
    # Replace with your actual Cloud Storage bucket name (e.g., your Baseball project bucket)
    bucket_name = "baseball_data_jpt"
    run_pipeline_for_yesterday(bucket_name)
