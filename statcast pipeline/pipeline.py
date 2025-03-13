# Packages / Libraries
import os
import io
from datetime import datetime, timedelta
import pandas as pd
import pybaseball
from pybaseball import statcast
from google.cloud import bigquery
from google.cloud import storage

#1. Determine date for which to pull data (here: yesterday)
today = datetime.today()
yesterday = today - timedelta(days=1)
start_date = yesterday.strftime('%Y-%m-%d')
end_date = start_date # One day range

print(f"Retrieving Statcast data for {start_date}")

#2. Pull data
try:
    data = statcast(start_dt=start_date, end_dt=end_date)
except Exception as e:
    print("Error retrieving data:", e)
    exit(1)

if data.empty:
    print("No data retrieved for", start_date)
    exit(0)

print(f"Retrieved {len(data)} rows of data.")

#3. Convert dataframe to CSV in-memory using StringIO
csv_buffer = io.StringIO()
data.to_csv(csv_buffer, index=False)
csv_contents = csv_buffer.getvalue()

#4. Upload the CSV data directly to Google Cloud Storage
bucket_name = "baseball_data_jpt"
filename = f"pitch_by_pitch_{start_date}.csv"

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(filename)

# Upload CSV data from in-mem string
blob.upload_from_string(csv_contents, content_type='text/csv')
print(f"CSV data for {start_date} successfully uploaded to bucket {bucket_name} as {filename}.")
